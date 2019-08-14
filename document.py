#!/usr/bin/python
# File Name : document.py
# Purpose : Document class to handle various aspects in a given document.
# Creation Date : 08-24-2011
# Last Modified : Thu 13 Jun 2013 09:08:15 AM MDT
# Created By : Nathan Gilbert
#
# TODO: text tile segmentation still fails on some texts (ace 03)
import sys
import nltk
import string
from nltk.corpus import stopwords

from . import reconcile
from .annotation_set import AnnotationSet
from .annotation import Annotation
from . import utils

class Document:
    def __init__(self, d):
        self.doc = d
        self.tiles = AnnotationSet("TextTiles")
        self.props = None
        self.text = ""
        self.normalizedText = ""
        self.gold_markables_by_span = []
        self.gold_chains = {}

        #the set of annotations duncan annotats
        self.duncan_annotations = None
        self.duncan_pairs = []

        self.nps = reconcile.getNPs_annots(self.doc)
        self.tokens = reconcile.getTokens(self.doc)
        self.verbs = reconcile.getVerbs(self.doc)
        self.preps = reconcile.getPreps(self.doc)
        self.pos = reconcile.getPOS(self.doc)
        self.sentences = reconcile.getSentences(d)

        #self.heidel = reconcile.getHeidelTime(d)
        #self.pdtb = reconcile.getPDTB(d)
        #self.pre_contexts = reconcile.getPreContexts(d)
        #self.post_contexts = reconcile.getPostContexts(d)
        #self.heads = reconcile.getHeads(d)

        #load in the text file
        self._getText()
        self._getNormalizedText()

        #process the document in various ways
        #get the TextTile output
        #self._getTextTiles()

    def getName(self):
        return self.doc

    def _getText(self):
        inFile = open(self.doc+"/raw.txt", 'r')
        allLines = ''.join(inFile.readlines())
        inFile.close()
        self.text = allLines
        tokens = nltk.word_tokenize(allLines)
        self.props = nltk.Text(tokens)

    def getText(self):
        return self.text

    def getTokens(self):
        return self.tokens

    def isNoun(self, annot):
        """returns true if annotation contains only nouns and dets"""

        overlap = self.pos.getOverlapping(annot)
        for p in overlap:
            if not p.getATTR("TAG").startswith("NN") \
                    or not p.getATTR("TAG").startswith("DT"):
                return False

        return True

    def getSubjectVerb(self, annot):
        """
            Finds the verb that the give annot is a subject of
        """
        for verb in self.verbs:
            if verb.getStart() > annot.getEnd() and verb.getEnd() > annot.getEnd():
                return verb

    def getVerbPhrase(self, verb):
        """
        returns the text of a verb phrase (multiple verb tokens side by side)
        """
        phrase = []
        i = 0
        for tag in self.pos:
            if tag == verb:
                break
            i += 1
        if self.pos.container[i-1].getATTR("TAG").startswith("V"):
            phrase.append(self.pos.container[i-1])
        phrase.append(verb)
        if len(self.pos) > i+1 and self.pos.container[i+1].getATTR("TAG").startswith("V"):
            phrase.append(self.pos.container[i+1])
        return phrase

    def getPostMods(self, annot):
        """
            return the text of a prep phrase
        """
        phrase = []
        i=0
        for tag in self.pos:
            i+=1
            if tag == annot:
                break
        if len(self.pos) > i+1:
            next_tag = self.pos.container[i]
            if next_tag.getATTR("TAG") == "IN":
                phrase.append(next_tag)
                for tag in self.pos.container[i+1:]:
                    if tag.getATTR("TAG") == "DT"\
                            or tag.getATTR("TAG").startswith("JJ")\
                            or tag.getATTR("TAG").startswith("NN"):
                        phrase.append(tag)
                    else:
                        break

        if len(phrase) == 0:
            return None
        else:
            return ' '.join([x.getText() for x in phrase])

    def getObjectVerb(self, annot):
        """
            return the verb that this annot is the object of
        """
        obj_verb = None
        for verb in self.verbs:
            if verb.getEnd() > annot.getStart() or verb.getEnd() > annot.getStart():
                break
            obj_verb = verb
        return obj_verb

    def getVerbObject(self, verb):
        """
            return the object of the supplied verb
        """
        i=0
        for t in self.pos:
            if t.getStart() < verb.getEnd():
                i += 1
                continue
            else:
                break

        obj = []
        for tag in self.pos.container[i:]:
            if tag.getATTR("TAG") == "DT"\
                    or tag.getATTR("TAG").startswith("NN")\
                    or tag.getATTR("TAG").startswith("JJ"):
                obj.append(tag)
            else:
                break

        if obj == []:
            return None
        else:
            return ' '.join([x.getText() for x in obj])

    def getPreceedingNoun(self, annot):
        prev_tokens = []
        for t in self.pos:
            if t.getStart() >= annot.getStart():
                break
            prev_tokens.append(t)
        prev_tokens.reverse()

        end = -1
        start = -1
        a_id = 0
        a = None
        for t in prev_tokens:
            if t.getATTR("TAG").startswith("NN") and end == -1:
                end = t.getEnd()
                start = t.getStart()
            elif t.getATTR("TAG").startswith("NN"):
                start = t.getStart()
            else:
                if start != -1 and end != -1:
                    text = self.text[start:end]
                    a = Annotation(start, end, a_id, {}, text)
                    a_id += 1
                break
        return a

    def getPreceedingAdj(self, annot):
        """
        Takes an annotation, and returns any adjectives that directly precede
        that annotation in the text.
        """
        prev_tokens = []
        for t in self.pos:
            if t.getStart() >= annot.getStart():
                break
            prev_tokens.append(t)
        prev_tokens.reverse()

        end = -1
        start = -1
        a_id = 0
        a = None
        for t in prev_tokens:
            if t.getATTR("TAG").startswith("JJ") and end == -1:
                end = t.getEnd()
                start = t.getStart()
            elif t.getATTR("TAG").startswith("JJ"):
                start = t.getStart()
            else:
                if start != -1 and end != -1:
                    text = self.text[start:end]
                    a = Annotation(start, end, a_id, {}, text)
                    a_id += 1
                break
        return a

    def getContainedTime(self, annot):
        """
        return any time annotations that contain this annotation
        """
        for t in self.heidel:
            if t.contains(annot) or annot.contains(t):
                return t
        return None

    def getContainedPDTB(self, annot):
        contained = self.pdtb.getContainedSet(annot)
        if len(contained) > 0:
            return contained
        else:
            return []

    def getPDTBLabel(self, label):
        for annot in self.pdtb:
            if annot.getATTR("SID") == label\
                    and not annot.getATTR("LABEL").startswith("Arg"):
                return "%s:%s" % (annot.getATTR("LABEL"),
                        annot.getATTR("SUBLABEL"))
        return None

    def getContainedAdj(self, annot):
        """
        Takes an annotation and returns any adjectives found inside it.
        """
        overlap = [x for x in self.pos.getOverlapping(annot) if x.getATTR("TAG").startswith("JJ")]
        if len(overlap) < 1:
            return None
        else:
            return overlap

    def getContainedMods(self, annot):
        """
        returns modifiers in an annots text.
        NNP NNP NN -> NNP NNP
        NN NNP NNP NNP -> NN
        """
        np_pos = [x.getATTR("TAG") for x in self.pos.getOverlapping(annot)]
        np_tok = [x.getText() for x in self.tokens.getOverlapping(annot)]
        annot.setProp("TAGS", np_pos)
        annot.setProp("TOKENS", np_tok)
        #overlap = self.pos.getOverlapping(annot)
        mods = utils.getMods(annot)

        if mods.strip() == '':
            return None
        else:
            return mods

    def _getNormalizedText(self):
        """Gets text will all newlines removed"""
        self.normalizedText = self.text.replace("\n", " ")
        self.normalizedText = ' '.join(self.normalizedText.split())

    def addDuncanPair(self, antecedent, anaphor, h):
        """adds the pair to the duncan annotations"""
        self.duncan_pairs.append((antecedent, anaphor, h))

        if self.duncan_annotations is None:
            self.duncan_annotations = AnnotationSet("duncan annots")

        if antecedent in self.duncan_annotations:
            ref_id = \
            self.duncan_annotations.getAnnotBySpan(antecedent.getStart(),
                    antecedent.getEnd()).getID()
            anaphor.setProp("REF", ref_id)
            self.duncan_annotations.add(anaphor)

    def getDuncanPairs(self):
        """ """
        return self.duncan_pairs

    def getPhraseCount(self, phrase):
        """ """
        #TODO note: it does not take into account substring, such 
        #as "the country" will match "the country's", etc.
        return self.text.count(phrase)

    def addGoldChains(self, gc):
        self.gold_chains = gc
        annots = AnnotationSet("tmp")
        for chain in list(gc.keys()):
            for mention in gc[chain]:
                annots.add(mention)
        self.gold_markables_by_span = annots.getList()

    def closest_antecedent(self, mention):
        """returns the closest antecedent in the text. if base antecedent,
        returns None"""
        #find this mention in gold chains
        for key in list(self.gold_chains.keys()):
            prev = None
            for other in self.gold_chains[key]:
                if mention == other:
                    return prev
                else:
                    prev = other
        return None

    def allPreviousGoldMarkables(self, otherMarkable, goBack=-1):
        """returns all gold markables that appear in a document prior to the
        given markable."""
        if self.gold_markables_by_span == []:
            return []

        #get the markables sentence
        s = self.getAnnotSentence(otherMarkable)
        target_s = s - goBack

        prev_marks = []
        if goBack < 0 or target_s < 0:
            for mark in self.gold_markables_by_span:
                if mark.getStart() >= otherMarkable.getStart():
                    break
                prev_marks.append(mark)
        else:
            #target_s is > 0
            for mark in self.gold_markables_by_span:
                mark_s = getAnnotSentence(mark)
                #if the antecedent is outside of the range, don't add it to the
                #list.
                if (mark_s < target_s):
                    continue
                if (mark.getStart() >= otherMarkable.getStart()):
                    break
                prev_marks.append(mark)
        return prev_marks

    def getContainedMarkables(self, sent):
        marks = AnnotationSet("markables in sentence")
        for np in self.nps:
            if sent.contains(np):
                marks.add(np)
        return marks

    def previousPrep(self, markable):
        """
        Returns the prep (if any) before the given markable, the criteria
        allows determiners, adjectives and other nouns (modifiers) ahead of the markable,
        but anything else breaks the search
        """
        allowedPOS = ("JJ", "JJR", "JJS", "NN", "NP", "CD", "DT" )
        preps = ("IN", "AT")

        start = None
        for pos in self.pos:
            if pos.getStart() == markable.getStart():
                #this is the start of the markable in question
                start = pos

        if start is None:
            return None

        #get all the POS starting at the current start (so we're looking back
        #at the beginning
        allPOS = self.pos.getList()[:self.pos.getList().index(start)]
        allPOS.reverse()
        for pos in allPOS:
            if (pos.getATTR("TAG") in allowedPOS):
                continue
            elif (pos.getATTR("TAG") in preps):
                return pos
            else:
                return None

    def getMiddleWords(self, annot1, annot2):
        """Returns all the intermediate words between the given two
        annotations."""
        words = self.text[annot1.getEnd()+1:annot2.getStart()-1].replace("\n",
                " ").replace(":","$COLON$").strip()

        if words == "":
            words = "$!$->%s" % (self.text[annot1.getStart():annot1.getEnd()])

        return words.replace("\n", " ")

    def getMiddleWords2(self, annot1, annot2):
        words = self.text[annot1.getEnd()+1:annot2.getStart()-1].replace("\n",
                " ").strip()
        return words

    def getWordCounts(self, word):
        """Returns the total number occurrences of a given string"""
        return self.props.count(word)

    def inParen(self, annot):
        """Returns true is the annotation is enclosed in parenthesis"""
        try:
            new_string = self.text[annot.getStart()-1:annot.getEnd()+1]
        except:
            new_string = ""

        if new_string == "("+annot.getText()+")":
            return True

        return False

    def findAllInstances(markable):
        """
         Finds all instances in the text of a given markable
        """
        #TODO - this is surprisingly hard given all the substring, end,
        #beginning of sentence demarcations
        markable_text = markable.getText()
        starts = [match.start() for match in \
                re.finditer(re.escape(markable_text), self.normalizedText)]

    def getContextWindowPre(self, annot, windowSize=3):
        """Return a context window of prescribed size around the given
        annotation."""

        sent = self.sentences.getList()[self.getAnnotSentence(annot)]
        tokens = [t.getText() for t in self.tokens if t.getStart() >= \
                sent.getStart() and t.getEnd() < annot.getStart()]

        if len(tokens) < windowSize:
            while len(tokens) < windowSize:
                tokens.insert(0, "$$")
        else:
            #we need to shrink it...
            tokens = tokens[-windowSize:]

        #tokens = [t.getText() for t in self.tokens if t.getEnd() < annot.getStart()]
        return tokens

    def getContextWindowPost(self, annot, windowSize=3):
        """Return a context window of prescribed size around the given
        annotation."""
        sent = self.sentences.getList()[self.getAnnotSentence(annot)]
        tokens = [t.getText() for t in self.tokens if t.getStart() > \
                annot.getEnd() and t.getEnd() < sent.getEnd()]

        if len(tokens) < windowSize:
            while len(tokens) < windowSize:
                tokens.append("$$")
        else:
            tokens = tokens[:windowSize]
        #tokens = [t.getText() for t in self.tokens if t.getStart() > annot.getEnd()]
        #return tokens[:windowSize]
        return tokens

    def _getTextTiles(self):
        """Segment the document """
        tiler = nltk.tokenize.TextTilingTokenizer()
        try:
            tokens = tiler.tokenize(self.text)
        except:
            tokens = [self.text]

        for t in tokens:
            #getting the bytespans
            start = self.text.find(t)
            end = start + len(t)
            props = {}
            t_annot = Annotation(start, end, tokens.index(t), props, t)
            self.tiles.add(t_annot)

    def getAnnotTile(self, annot):
        """return the annotation tile number."""
        i=0
        for t in self.tiles:
            if t.contains(annot):
                return i
            i+=1
        return -1

    def getAnnotSentence(self, annot):
        i=0
        for t in self.sentences:
            if t.contains(annot):
                return i
            i+=1

        #if we didn't find it outright in one of the sentences, let's try to
        #find one where this mention starts...
        i = 0
        for sent in self.sentences:
            if annot.getStart() <= sent.getEnd():
                return i
            i+=1

        #we still couldn't find anything...
        sys.stderr.write("error: couldn't find sentence number for {0}".format(annot.ppprint()))
        return -1

    def getNGramWindow(self, annot, pre=True, n=5):
        """Returns a set of context words preceding a given antecedent"""
        if pre:
            window = self.getContextWindowPre(annot, n)
        else:
            window = self.getContextWindowPost(annot, n)

        final = []
        for token in window:
            #lower case
            token = token.lower()

            #keep sentence markers
            if token == "$$":
                final.append(token)
                continue

            #remove punct and stop words
            if (token.lower() in stopwords.words('english')) \
                    or (token in string.punctuation):
                continue

            final.append(token)
        final = "_".join(final)
        return final

    def getSingletonCount(self, text):
        """
        Returns the number of times the text in the annotation is found outside
        of the gold mentions.
        """
        #NOTE currently only works with single word phrases [like pronouns]
        n_text_tokens = self.normalizedText.lower().split()
        a_text = utils.textClean(text.lower())
        count = 0
        for word in n_text_tokens:
            #NOTE There may be more of these instances where 
            #some string manipulation is required to match strings.
            word = word.replace("\"","")
            if word == a_text:
                count += 1
        #print count

        #remove instances that are also found in the gold mentions
        for g_np in self.gold_markables_by_span:
            if utils.textClean(g_np.getText().lower()) == a_text:
                count -= 1

        if count < 0:
            #sys.stderr.write("Negative string count: {0}".format(text))
            count = 0
        #print count
        return count

    def __str__(self):
        return self.doc

    def getPath(self):
        return self.doc

    def close(self):
        self.doc = None
        self.tiles = None
        self.props = None
        self.text = ""
        self.normalizedText = ""
        self.gold_markables_by_span = []

        #all the parts of speech as supplied by Reconcile
        self.sentences = None

        #the set of annotations duncan annotats
        self.duncan_annotations = None
        self.duncan_pairs = None

        #the set of nps that Reconcile annotated
        self.nps = None
        self.tokens = None
        self.verbs = None
        self.preps = None
        self.pos = None

    def word_distance(self, annot1, annot2):
        """
        The distance in words between these two annotations.

        Annot1 is assumed to be the one earliest in the document.
        """
        if annot1.getEnd() > annot2.getStart():
            return 0

        in_between_text = self.text[annot1.getEnd():annot2.getStart()]
        tokens = in_between_text.split()
        return len(tokens)

    def sentence_distance(self, annot1, annot2):
        """
        Returns the distance in sentences from annot1 (the earliest/antecedent)
        and annot2 (the anaphor)
        """
        sent1 = self.getAnnotSentence(annot1)
        sent2 = self.getAnnotSentence(annot2)

        #if sent1 < 0 or sent2 < 0:
        #    print self.doc

        if sent1 > sent2:
            return sent1 - sent2
        else:
            return sent2 - sent1
        #return 10**6 #infty

if __name__ == "__main__":
    doc = "/home/nathan/Documents/data/muc6-train/1"
    d = Document(doc)
    gold_chains = reconcile.getGoldChains(doc)
    d.addGoldChains(gold_chains)
    i = d.getSingletonCount("it")
