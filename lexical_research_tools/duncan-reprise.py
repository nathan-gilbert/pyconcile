#!/usr/bin/python
# File Name : duncan_reprise.py
# Purpose : This is Duncan/David Bean's work reinterpreted. 
# Creation Date : 12-06-2011
# Last Modified : Thu 20 Jun 2013 05:48:23 PM MDT
# Created By : Nathan Gilbert
#
#from David's original paper...
#DONE Reflexive pronouns heuristic
#DONE Relative pronoun heuristic
#DONE NP to-be NP
#DONE NP *said* X
#TODO Locative
#DONE Appositives
#TODO PPs containing "by" and a gerund followed by "it"
#DONE string match/head match
#DONE Acronym matcher
#TODO First sentence heuristic
import sys
import time
from optparse import OptionParser
from collections import defaultdict

import nltk

from pyconcile.annotation import Annotation
from pyconcile.annotation_set import AnnotationSet
from pyconcile import duncan
from pyconcile import reconcile
from pyconcile import data
from pyconcile import utils
from pyconcile import feature_utils
from pyconcile.document import Document
from pyconcile import string_match

VERBOSE=False

def is_MUC4_date(s):
    tokens = s.split()
    if len(tokens) == 3:
        if is_number(tokens[0]) and is_number(tokens[2]):
            if tokens[1] in data.muc4_months:
                return True
    return False

def is_number(s):
    try:
        float(s)
        return True
    except:
        return False

def contains_number(s):
    for ch in s:
        if is_number(ch):
            return True
    return False

def reflexive_heuristic(doc):
    """
        This heuristic matches reflexive pronouns with the only NP that is in
        scope.
        '*The regime* gives *itself* the right...'
        Reflexive pronouns are primarily used in three situations: when the subject
        and object are the same (e.g., "He watched himself on TV."), as the object
        of a preposition when the subject and the object are the same
        (e.g., "That man is talking to himself."), and to emphasize the
        subject through an intensive pronoun (e.g., "They ate all the food themselves.")
    """
    for np in doc.nps:
        #find the reflexive
        if np.getText().lower() in data.REFLEXIVES:
            #possible anaphor
            anaphor = np

            #look back for the subject of the closest verb.
            r_sent = reconcile.getAnnotSentence(doc.getPath(), np)
            marks_in_sent = doc.getContainedMarkables(r_sent)

            antecedent = None
            for m in marks_in_sent:
                if m.getEnd() >= anaphor.getStart():
                    break

                #grab the last antecedent before reflexive that is the subject
                #of the sentence/clause
                if m.getATTR("GRAMMAR").startswith("SUBJ"):
                    if antecedent is None:
                        antecedent = m
                    elif m.getEnd() > antecedent.getEnd():
                        antecedent = m

            if antecedent is not None:
                #check for number/gender consistencies?
                #make the resolution
                if VERBOSE:
                    print("Heuristic 1: %s <- %s" % (antecedent.pprint(),
                            anaphor.pprint()))
                doc.addDuncanPair(antecedent, anaphor, "1")

def relative_heuristic(doc):
    """
    Relative pronouns with only one NP in scope.
    The brigade, which...

    MUC guidelines do not annotate reflexive pronouns.
    ACE guidelines do
    """
    for np in doc.nps:
        if np.getATTR("TEXT_LOWER") in data.relatives:
            anaphor = np

            #look back for the subject of the closest verb.
            r_sent = reconcile.getAnnotSentence(doc.getPath(), np)
            previous_marks = [x for x in doc.getContainedMarkables(r_sent).getList() if x.getStart() >=
                    anaphor.getStart()]

            #find the biggest NP preceding the relative, if there is only a
            #single NP then say they are coreferent
            if len(previous_marks):
                antecedent = previous_marks[0]
                if VERBOSE:
                    print("Heuristic 2: %s <- %s" % (antecedent.pprint(),
                            anaphor.pprint()))
                doc.addDuncanPair(antecedent, anaphor, "2")

def predicate_nominal_heuristic(doc, features):
    """
        Cases of NP to-be NP
        Mr X. is the president
    """
    #grab the features produced by Reconcile under features.default
    #if PredicateNominal is true, add them to the annotations
    for key in features:
        if features[key].get("Prednom", 0.0) > 0:
            antecedent = doc.nps.getAnnotByID(int(features[key]["ID1"]))
            anaphor = doc.nps.getAnnotByID(int(features[key]["ID2"]))

            #look for other cases, but filter out demonstratives and relatives from
            #being NP1
            #if antecedent.getText().lower() in ("it"):
            #    continue

            if antecedent.getATTR("TEXT_LOWER") in data.demonstratives \
                or antecedent.getATTR("TEXT_LOWER") in data.relatives:
                continue

            #don't allow linkings with indefinites?
            if anaphor.getATTR("is_indefinite"):
                continue

            if anaphor.getATTR("is_date") and not antecedent.getATTR("is_date"):
                continue

            #attempt to remove meronyms 
            if anaphor.getText().lower().find("part") > -1:
                continue

            #some markable extraction problems
            if anaphor.getText().lower().strip() in ("the"):
                continue

            if VERBOSE:
                print("Heuristic 3: %s <- %s" % (antecedent.pprint(),
                        anaphor.pprint()))
            doc.addDuncanPair(antecedent, anaphor, "3")

    #copular_verbs = doc.getCopularVerbs()
    #for copular in copular_verbs:

def Xsaid_heuristic(doc):
    """
    *The government* said *it*
    NP said pronoun
    """
    #find any mentions of said
    for v in doc.verbs:
        anaphor = None
        antecedent = None
        if v.getText() == "said":
            for np in doc.nps:
                #get the previous np
                if np.getEnd() < v.getStart():
                    if antecedent is None:
                        antecedent = np
                    elif np.getEnd() > antecedent.getEnd():
                        antecedent = np
                else:
                    #get following np
                    if np.getStart() > v.getEnd() and np.getATTR("TEXT_LOWER") in ("it",
                            "they", "he", "she"):
                        anaphor = np
                    else:
                        break

            if antecedent is not None and anaphor is not None:
                if VERBOSE:
                    print("Heuristic 4: %s <- %s" % (antecedent.pprint(),
                            anaphor.pprint()))
                doc.addDuncanPair(antecedent, anaphor, "4")

def locative_relative(doc):
    """
    Cases of [Locative-prep] NP [,] where
    """
    #TODO
    pass

def simple_appositive_heuristic(doc, features):
    """
    NP, NP
    """
    for key in features:
        if features[key].get("Appositive", 0.0) > 0:
            antecedent = doc.nps.getAnnotByID(int(features[key]["ID1"]))
            anaphor = doc.nps.getAnnotByID(int(features[key]["ID2"]))

            #don't allow linkings with indefinites?
            #if anaphor.getATTR("is_indefinite"):
            #    continue
            if anaphor.getATTR("is_date") and not antecedent.getATTR("is_date"):
                continue

            if is_MUC4_date(anaphor.getText()) \
                    and not is_MUC4_date(antecedent.getText()):
                continue

            if VERBOSE:
                print("Heuristic 6: %s <- %s" % (antecedent.pprint(),
                        anaphor.pprint()))
            doc.addDuncanPair(antecedent, anaphor, "6")

def pos_appositive_heuristic(doc):
    """
    look for:
     (a) DT+ NN, DT+ NN
    """

    #cycle over the POS tags
    for i in range(0, len(doc.pos)):
        np1 = ""
        np2 = ""
        np1_start = -1
        np1_end = -1
        np2_start = -1
        np2_end = -1
        comma = doc.pos[i]
        if comma.getATTR("TAG") == ",":
            #go back and find what came before
            for j in range(i-1,-1,-1):
                if doc.pos[j].getATTR("TAG") in ("DT", "NN", "NNP"):
                    np1 = doc.pos[j].getATTR("TAG") + " " + np1
                    if np1_end == -1:
                        np1_end = doc.pos[j].getEnd()
                    np1_start = doc.pos[j].getStart()
                else:
                    break

            #go forward and see what comes after
            found_det = True
            found_noun = False
            for j in range(i+1, len(doc.pos)):
                if found_det and doc.pos[j].getATTR("TAG") in ("DT"):
                    np2 = np2 + " " + doc.pos[j].getATTR("TAG")
                    if np2_start == -1:
                        np2_start = doc.pos[j].getStart()
                    np2_end = doc.pos[j].getEnd()
                    found_det = False
                elif doc.pos[j].getATTR("TAG") in ("NN") and np2 != "":
                    np2 = np2 + " " + doc.pos[j].getATTR("TAG")
                    if np2_start == -1:
                        np2_start = doc.pos[j].getStart()
                    np2_end = doc.pos[j].getEnd()
                    found_noun = True
                else:
                    break

            np1 = np1.strip()
            np2 = np2.strip()
            np1_text = doc.getText()[np1_start:np1_end].replace("\n", " ")
            np2_text = doc.getText()[np2_start:np2_end].replace("\n", " ")
            if np1 != "" and np2 != "" and found_noun:
            #    print "{0}, {1}".format(np1_text, np2_text)
                antecedent = Annotation(np1_start, np1_end, 0, {}, np1_text)
                anaphor = Annotation(np2_start, np2_end, 1, {}, np2_text)
                if VERBOSE:
                    print("Heuristic 6b: %s <- %s" % (antecedent.pprint(),
                            anaphor.pprint()))
                doc.addDuncanPair(antecedent, anaphor, "6b")

def prep_by_heuristic(doc):
    """
    PPs containing by and a gerund followed by 'it'
    Mr. Bush disclosed *the policy* by reading *it*
    """
    #get preps
    for p in doc.preps:
        if p.getText() in ("by"):
            #get the previous np
            antecedent = doc.nps.getPreviousAnnot(p)

            #is it followed by a gerund?
            next_token = doc.pos.getNextAnnot(p)
            if next_token.getATTR("TAG") == "VBG":
                #is this token followed by it?
                anaphor = doc.nps.getNextAnnot(next_token)
                if anaphor.getText() in ("it"):
                    #make the resolution
                    if VERBOSE:
                        print("Heuristic 7: %s <- %s" % (antecedent.pprint(),
                                anaphor.pprint()))
                    doc.addDuncanPair(antecedent, anaphor, "7")

def stringmatch_heuristic(doc):
    """Implements string match heuristic"""
    nps = doc.nps.getList()
    for i in range(len(nps) - 1, 1, -1):
        anaphor = nps[i]
        if not anaphor.getATTR("is_proper"):
            continue
        for j in range(i-1, 0, -1):
            antecedent = nps[j]
            if not antecedent.getATTR("is_proper"):
                continue

            if string_match.soon_match(antecedent.getText(), anaphor.getText()):
                if VERBOSE:
                    print("Heuristic 8: %s <- %s" % (antecedent.pprint(),
                            anaphor.pprint()))
                doc.addDuncanPair(antecedent, anaphor, "8")

def acronym_heuristic(doc):
    """
    Attempting to match things like USA <- United States of America
    """
    nps = doc.nps.getList()
    for i in range(len(nps) - 1, 1, -1):
        anaphor = nps[i]
        if not anaphor.getATTR("is_proper"):
            continue
        for j in range(i-1, 0, -1):
            antecedent = nps[j]
            if not antecedent.getATTR("is_proper"):
                continue

            if string_match.isAcronym(antecedent.getText(), anaphor.getText())\
                    or string_match.isAcronym(anaphor.getText(),
                            antecedent.getText()):
                if VERBOSE:
                    print("Heuristic 9a: %s <- %s" % (antecedent.pprint(),
                            anaphor.pprint()))
                doc.addDuncanPair(antecedent, anaphor, "9")

def acronym_heuristic2(doc):
    """
    This heuristic is specific to Promed, looking for instances of:
        foot-&-mouth disease (FMD)
        _Mycobacterium bovis_ (_M. bovis_)

        NOTE: creates new annotations, so throws the id system off created by
        Reconcile
    """
    #TODO doesn't handles cases where there is not a well-formed parenthesis
    #very cleverly.
    text = doc.getText()
    paren_texts = AnnotationSet("parens")
    latest = ""
    capture = False
    i = 0
    a_id = 0
    start = -1
    end = -1
    for t in text:
        if t == "(":
            start = i
            capture = True

        if capture:
            latest+= t

        if t == ")":
            end = i
            if start < 0:
                continue
            paren_texts.add(Annotation(start, end, a_id, {}, latest))
            a_id+=1
            latest=""
            capture = False
        i += 1

    for t in paren_texts:
        new_t = t.getText().replace("(","").replace(")", "")
        if contains_number(new_t):
            continue
        anaphor = Annotation(t.getStart()+1, t.getEnd(), t.getID(), {},
                t.getText().replace("(","").replace(")",""))
        if not doc.isNoun(anaphor):
            continue

        antecedent = doc.getPreceedingNoun(t)
        if antecedent is not None and len(anaphor.getText()) > 1:
            #print "%s <- %s" % (doc.getPreceedingNoun(t).getText(), t.getText())
            #make the resolution?
            if VERBOSE:
                print("Heuristic 9b: %s <- %s" % (antecedent.pprint(),
                        anaphor.pprint()))
            doc.addDuncanPair(antecedent, anaphor, "9b")

def acronym_heuristic3(doc, features):
    """
    Uses the Reconcile Alias feature...
    """
    for key in features:
        if features[key].get("Alias", 0.0) > 0:
            antecedent = doc.nps.getAnnotByID(int(features[key]["ID1"]))
            anaphor = doc.nps.getAnnotByID(int(features[key]["ID2"]))

            if antecedent.getText().lower() == anaphor.getText().lower():
                continue

            if VERBOSE:
                print("Heuristic 9c: %s <- %s" % (antecedent.pprint(),
                        anaphor.pprint()))
            doc.addDuncanPair(antecedent, anaphor, "9c")

def firstsentence_heuristic(doc):
    """
    Instances where there is only one possible antecedent for a given pronouns.
    Music is one of [Nathan]'s blah blah. [He] listens to it every day...
    """
    #TODO
    pass

def firstsentence_semantic_heuristics(doc):
    """
    Use the Sundance semantic tagger.
    Box in common->proper and common->common NPs if they appear with in a very
    small window at the beginning of the document.

    1. start with matching semantic classes
    2. the next step would be to incorporate semantic classes we know are
    coreferent via our annotated data
    """
    #these two semantic class cannot corefer
    EXCLUDE_LIST = ("STATE", "COUNTRY")

    if len(doc.sentences) < 2:
        return

    sentence1 = doc.sentences[0]
    sentence2 = doc.sentences[1]
    sundance_nes = reconcile.getSundanceNEs(doc.getName())

    first_sentence_nes = []
    second_sentence_nes = []
    for ne in sundance_nes:
        if sentence1.contains(ne):
            first_sentence_nes.append(ne)

        if sentence2.contains(ne):
            second_sentence_nes.append(ne)

    for ne1 in first_sentence_nes:
        for ne in  ne1.getATTR("SUN_NE"):
            if ne in EXCLUDE_LIST or ne.startswith("OTHER"):
                continue

        for ne2 in second_sentence_nes:
            if ne1.getATTR("SUN_NE")[0] == ne2.getATTR("SUN_NE")[0]:
                np1 = doc.getText()[ne1.getStart():ne1.getEnd()+1]
                np2 = doc.getText()[ne2.getStart():ne2.getEnd()+1]
                if np1.lower() != np2.lower():
                    #print "{0} <- {1} : {2}".format(np1,np2,ne1.getATTR("SUN_NE")[0])
                    antecedent = Annotation(ne1.getStart(), ne1.getEnd()+1, 0, {}, np1)
                    anaphor = Annotation(ne2.getStart(), ne2.getEnd()+1, 1, {}, np2)
                    if VERBOSE:
                        print("Heuristic 10: %s <- %s" % (antecedent.pprint(),
                                anaphor.pprint()))
                    doc.addDuncanPair(antecedent, anaphor, "10")

def pdtb_parser_results(doc):
    """
    Captures pairs that indicate coreference based on the output of the PDTB
    discourse parser.
    """
    #TODO
    pass


def process_doc(doc, options):
    """Processes a doc with the specific heuristics"""

    if options.all:
        features = feature_utils.getFeatures(d.getPath(), "features.default", ("Prednom", "Appositive", "Alias"))
        #reflexive_heuristic(d)
        ##relative_heuristic(d)
        predicate_nominal_heuristic(d,features)
        #predicate_nominal_heuristic2(d,features)
        #Xsaid_heuristic(d)
        simple_appositive_heuristic(d, features)
        pos_appositive_heuristic(d)
        #prep_by_heuristic(d)
        #stringmatch_heuristic(d)
        #firstsentence_heuristic(d)
        acronym_heuristic(d)
        acronym_heuristic2(d)
        acronym_heuristic3(d, features)
        firstsentence_semantic_heuristics(d)
    if options.write:
        output(d)
    numer_of_pairs = len(d.getDuncanPairs())
    d.close()
    return numer_of_pairs

def output(doc):
    """Write out the document in the proper format"""
    pairs = doc.duncan_pairs

    #find duplicates
    heurs = defaultdict(list)
    for i in range(0, len(pairs)):
        curr = pairs[i]
        byte = (curr[0].getStart(), curr[0].getEnd(), curr[1].getStart(),
                curr[1].getEnd())
        h = curr[2]
        if h not in heurs.get(byte, []):
            heurs[byte].append(h)

    outFile = open(doc.getPath() + "/annotations/duncan2", 'w')
    i = 0
    written = []
    for p in pairs:
        antecedent = p[0]
        anaphor = p[1]
        byte = (antecedent.getStart(), antecedent.getEnd(),
                anaphor.getStart(), anaphor.getEnd())
        if byte not in written:
            written.append(byte)
        else:
            #then we've already printed this pair
            continue
        h = ','.join([str(x) for x in heurs[byte]])
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t\n" % (i,
            antecedent.getStart(), antecedent.getEnd(), i))
        i += 1
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%d\"\tH=\"%s\"\n" % (i,
            anaphor.getStart(), anaphor.getEnd(), i,i-1,h))
        i += 1
    outFile.close()

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filelist", dest="filelist",
            help="A list of directories to process", type="string",
            action="store", default=None)
    parser.add_option("-w", help="Write Reconcile output", action="store_true",
            dest="write", default=False)
    parser.add_option("-v", help="Verbosity", action="store_true",
            dest="verbose", default=False)
    parser.add_option("-a", help="Use all heuristics.", action="store_true",
            dest="all", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        VERBOSE=True

    if options.filelist is not None:
        fList = open(options.filelist, 'r')
        total_start_time = time.time()
        for f in fList:
            if f.startswith("#"):
                continue
            f=f.strip()
            start_time = time.time()
            print("Processing document: %s" % f)
            d = Document(f)
            num_pairs = process_doc(d, options)
            end_time = time.time()
            print("process time: %0.3f seconds :: %d pairs added" % ((end_time-start_time, num_pairs)))
        total_end_time = time.time()
        print("Total process time: %0.3f seconds" % ((total_end_time-total_start_time)))
