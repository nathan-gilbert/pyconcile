#!/usr/bin/python
# File Name : master_nominal_stats.py
# Purpose : The DEFINITIVE version of the nominal statistic generator. 
# Creation Date : 09-30-2011
# Last Modified : Fri 16 Dec 2011 12:47:09 PM MST
# Created By : Nathan Gilbert
#
import sys
import string
#from collections import Counter #not available in python 2.6.5
from collections import defaultdict
from optparse import OptionParser
import cPickle as pickle

from pyconcile import reconcile
from pyconcile.annotation import Annotation
from pyconcile.annotation_set import AnnotationSet
from pyconcile.document import Document
from pyconcile.nominal import Nominal
from pyconcile import data
import duncan_nominal_stats

#statistic to generate
#DONE 'virtual pronoun'(corefiness) stats 
#DONE 'base antecedent' stats
#DONE 'existential' stats <- currently, only gold existentials
#DONE probabilities for these
#DONE most likely semantic type resolution
#DONE avg # of appearances per doc
#DONE median # of appearances per doc
#DONE avg sentence distance from antecedent
#DONE median sentence distance from antecedent
#DONE text tile feature
#DONE antecedent type (prob and count)
#DONE discourse focus feature <- this is not necessarily statistics based.
#DONE count the number of times a certain pair has been seen as coreferent
#DONE the number of times a pair have been seen to be not coreferent
#DONE boxing in feature (doc location for nominals)
#DONE (a) most popular verbs
#DONE (b) adverbs and  
#DONE the semantic class for this common noun, propagated from chain. (similar to above.)
#TODO: is the anaphor coreferent with the previous word in the document?

#globals
VERBOSE = False
HEADS_ONLY = False

def output_to_human(db):
    for nom in db.keys():
        print db[nom]

def output_to_file(filename, db):
    """Outputs statistics to a file """
    outfile = open(filename, 'w')
    for nom in db.keys():
        outfile.write("%s\n" % (db[nom]))
        outfile.write("$!$\n")
    outfile.close()

def incrementDict(feature, ident, db):
    """Increments the given feature in the db by 1"""
    if ident in db.keys():
        db[ident].increment(feature)

def incrementCount(ident, db):
    if ident in db.keys():
        db[ident].incrementCount()

#def updatePrevTag(ident, tag, db):
#    if ident in db.keys():
#        db[ident].updateSemanticTags(tag)

#def updateSentence(ident, prev, current, db):
#    if prev > -1 and current > -1:
#        distance = current - prev
#        if ident in db.keys():
#            db[ident].sentence_distance.append(distance)

def updateLocationInDoc(ident, percentile_loc, db):
    if ident in db.keys():
        db[ident].doc_location.append(percentile_loc)

def updateTile(ident, prev, current, db):
    if prev > -1 and current > -1:
        if ident in db.keys():
            db[ident].text_tile_distance.append(current - prev)

def updateAnteType(ident, prev, db):
    if prev != "":
        if ident in db.keys():
            db[ident].updateAnteType(prev)

def makeNominal(ident, ft, doc, db):
    if ident not in db.keys():
        #make the nom
        nom = Nominal()
        nom.setText(ident)
        nom.addDoc(doc)
        nom.addFulltext(ft)
        db[ident] = nom
    else:
        db[ident].addDoc(doc)

def getMostCommonAntecedent(antecedents):
    """Returns the most common entity that is a possible antecedent for the
    given anaphor. Not necessarily coreferent.
    annotation set -> annotation"""
    global HEADS_ONLY

    #all the strings in the antecedents
    if HEADS_ONLY:
        strings = map(lambda x : x.getATTR("HEAD_TEXT").lower(), antecedents)
    else:
        strings = map(lambda x : x.getATTR("TEXT_CLEAN").lower(), antecedents)
    #most_common returns a list of tuples, grabbing first one
    #c = Counter(strings) #had to reimplement for python 2.6.5
    #most_common_antecedent = c.most_common(1)[0]
    top_count = -1
    top_string = ""
    for s in strings:
        if strings.count(s) > top_count:
            top_count = strings.count(s)
            top_string = s
    most_common_antecedent = top_string
    if most_common_antecedent != "":
        for a in antecedents:
            if HEADS_ONLY:
                if a.getATTR("HEAD_TEXT").lower() == most_common_antecedent[0]:
                    return a
            else:
                if a.getATTR("TEXT_CLEAN").lower() == most_common_antecedent[0]:
                    return a
    #should never happen, unless first NP in doc. 
    return Annotation(-1, -1, -1, {}, "")

def checkCoreferent(other, anaphor):
    """Checks whether two Gold NPs are in the same chain."""
    #this is only going to work if both annotations have a CorefID attr.

    if other is None or anaphor is None:
        return False

    if mention.getATTR("COREF_ID") == other.getATTR("COREF_ID"):
        return True
    else:
        return False

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filelist", help="List of files to process",
            action="store", dest="filelist", type="string", default="")
    parser.add_option("-v", "--verbose", help="Verbosity", action="store_true",
            dest="verbose", default=False)
    parser.add_option("-p", "--pickle-something", help="Pickle some preselected attributes",
            action="store_true", dest="pickle", default=False)
    parser.add_option("-w", "--write_stats", help="Write statistics to Reconcile readable file.",
            action="store_true", dest="write_stats",default=False)
    parser.add_option("-r", "--human-readable", help="Output stats in a human readable/unix sortable format",
            action="store_true", dest="pprint",default=False)
    parser.add_option("-o", "--out_file", help="The name of the features file",
            action="store", type="string", default="all-stats", dest="outfile")
    parser.add_option("-e", "--heads-only", help="Use the heads only for stat generation",
            action="store_true", dest="heads_only",default=False)
    parser.add_option("-d", "--duncan_files", help="Add statistics from duncan.",
            action="store", dest="duncan_files",default=None)
    (options, args) = parser.parse_args()

    if (len(sys.argv) < 2) or (options.filelist == ""):
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        VERBOSE = True

    if options.heads_only:
        HEADS_ONLY = True

    #the master dictionary of text to nominals 
    text2nominal = {}

    #something easy to pickle
    noun2antecedents = defaultdict(dict)

    fileList = open(options.filelist, 'r')
    #lines that start with # are ignored
    files = filter(lambda x : not x.startswith("#"), fileList.readlines())
    fileList.close()
    for f in files:
        f = f.strip()
        print "Working on document: %s" % f

        #load in the document statistics
        d = Document(f)

        #the total number of sentences in this text file. 
        #?double check with nltk?
        total_sentences_doc = len(reconcile.getSentences(f))

        #process a document, get all the nominal stats that are requested. 
        gold_chains = reconcile.getGoldChains(f, True)
        d.addGoldChains(gold_chains)

        for gc in gold_chains.keys():
            base_antecedent = True
            previous_semantic_tag = ""
            prev_sent = -1
            prev_tile = -1
            prev_type = ""

            for mention in gold_chains[gc]:
                if HEADS_ONLY:
                    head_clean = ' '.join(map(string.strip, \
                        mention.getATTR("HEAD_TEXT").split())).strip()
                    text_ident = head_clean.lower()
                    text_ident = mention.getATTR("HEAD_TEXT").strip().lower()
                else:
                    text_ident = mention.getATTR("TEXT_CLEAN").lower()

                if text_ident == "":
                    print "NULL Text: %s (%s)" % (mention.getText(), f)

                if mention.getATTR("is_nominal") or \
                mention.getATTR("is_proper") or mention.getATTR("is_pronoun"):
                    #if text_ident in data.ALL_PRONOUNS:
                    #    print "Doc: %s pronoun: %s gold_type: %s" % (f,
                    #            text_ident, mention.getATTR("GOLD_TYPE"))

                    #this creates the nominal if hasn't been yet.
                    makeNominal(text_ident, mention.text, f, text2nominal)

                    #grab the semantic tag of *this* nominal
                    #text2nominal[text_ident].updateThisSemantic(mention.getATTR("GOLD_SEMANTIC"))
                    for entry in mention.getATTR("SUN_SEMANTIC"):
                        text2nominal[text_ident].updateThisSemantic(entry)
                    #text2nominal[text_ident].updateSundanceMorph(mention.getATTR("SUN_MORPH"))
                    #text2nominal[text_ident].updateSundanceRole(mention.getATTR("SUN_ROLE"))

                    if base_antecedent:
                        if mention.getATTR("GOLD_SINGLETON"):
                            #this is a gold existential np
                            incrementDict("EXIST_COUNT", text_ident, text2nominal)
                        else:
                            #this is part of a chain, but is a base antecedent
                            incrementDict("BA_COUNT", text_ident, text2nominal)
                    else:
                        #we are not a base_antecedent, this is corefiness
                        incrementDict("COREF_COUNT", text_ident, text2nominal)

                        #capture the previous markable's semantic tag
                        text2nominal[text_ident].updateSemanticTags(previous_semantic_tag)

                        #keep track of any previous prepositional phrases
                        text2nominal[text_ident].updatePrevPreps(d.previousPrep(mention))

                        #get the sentence distance from these two mentions.
                        mention_sent = reconcile.getAnnotSentenceNum(f, mention)
                        if VERBOSE:
                            if mention_sent == -1:
                                print "%s sentence not found" % (text_ident)

                        if mention_sent > -1 and prev_sent > -1:
                            dist = mention_sent - prev_sent
                            text2nominal[text_ident].sentence_distance.append(dist)

                            if VERBOSE:
                                if dist < 0:
                                    print "Distance less than 0, current: %d \
                                    prev: %d" % (mention_sent, prev_sent)

                        #where in the doc does this mention occur
                        percentile_loc = float(mention_sent) / total_sentences_doc
                        updateLocationInDoc(text_ident, percentile_loc,
                                text2nominal)

                        #text tile distance
                        mention_tile = reconcile.getAnnotTile(f, mention)
                        updateTile(text_ident, prev_tile, mention_tile,
                                text2nominal)

                        #the previous semantic class
                        updateAnteType(text_ident, prev_type, text2nominal)

                        #keep track of all previous antecedents
                        #verified in debuggin, this looks to be working correctly. 10/29/11
                        previous_antecedents = d.allPreviousGoldMarkables(mention)

                        #what is the most common previous entity (not
                        #necessarily coreferent with this common noun
                        most_common_antecedent = \
                        getMostCommonAntecedent(previous_antecedents)

                        #is it coreferent with the most common entity?
                        #FOCUS1 => the # of times this nominal is coreferent
                        #with the most numerous NP is the document at this
                        #point.
                        if checkCoreferent(most_common_antecedent, mention):
                            text2nominal[text_ident].increment("FOCUS1")

                        #context switch verbs
                        # ENT_1 verb ENT_2, where 2 not coref with 1 and no
                        # coref entities appear between 1 & 2.
                        if len(previous_antecedents) > 0:
                            closest = previous_antecedents[-1]
                        else:
                            closest = None

                        #check to see if closest is actually the proceeding
                        #word/phrase
                        if closest is not None:
                            if checkCoreferent(closest, mention):
                                closest_sent = reconcile.getAnnotSentenceNum(f,closest)
                                if (closest_sent == mention_sent):
                                    #lets capture all the words between the closest 
                                    text2nominal[text_ident]\
                                            .updateIntermediateWords(\
                                            d.getMiddleWords(closest, mention))
                            else:
                                #if not checkCoreferent(closest, mention) and \
                                #        closest is not None:
                                #they are NOT coreferent, so now find any verbs
                                #that might be between them.
                                verbs = reconcile.getVerbs(f)
                                for v in verbs:
                                    if (v.getStart() > closest.getEnd()) and \
                                    (v.getEnd() < mention.getStart()):
                                        #this verb is between the two mentions.
                                        text2nominal[text_ident].updateSwitchVerbs(v.getText().lower())

                                #now the same thing with adverbs
                                adverbs = reconcile.getAdverbs(f)
                                for av in adverbs:
                                    if (av.getStart() > closest.getEnd()) and \
                                    (av.getEnd() < mention.getStart()):
                                        text2nominal[text_ident].updateSwitchAdverbs(av.getText().lower())

                        #update the current list of things that have been
                        #seen as coreferent and *NOT* be coreferent to 
                        #the current nominal
                        for prev in previous_antecedents:
                            if checkCoreferent(prev, mention):
                                if HEADS_ONLY:
                                    text2nominal[text_ident].updatePrevAntes(prev.getATTR("HEAD_TEXT").lower())
                                else:
                                    prev_text_ident = \
                                    prev.getATTR("TEXT_CLEAN").lower()
                                    text2nominal[text_ident].updatePrevAntes(prev_text_ident)
                                    if prev_text_ident != text_ident:
                                        noun2antecedents[text_ident][prev_text_ident]=\
                                                noun2antecedents.get(text_ident,{}).get(prev_text_ident,
                                                        0) + 1
                            else:
                                if HEADS_ONLY:
                                    if text_ident != prev.getATTR("HEAD_TEXT").lower():
                                        text2nominal[text_ident].updatePrevAntiAntes(prev.getATTR("HEAD_TEXT").lower())
                                else:
                                    if prev.getATTR("TEXT_CLEAN").find(text_ident) < 0:
                                        text2nominal[text_ident].updatePrevAntiAntes(prev.getATTR("TEXT_CLEAN").lower())

                    #update the counts for this nominal
                    incrementCount(text_ident, text2nominal)
                base_antecedent = False

                #previous_semantic_tag = mention.getATTR("GOLD_SEMANTIC")
                previous_semantic_tag = mention.getATTR("SUN_SEMANTIC")[0] if \
                mention.getATTR("SUN_SEMANTIC") != "" else "UNKNOWN"

                prev_sent = reconcile.getAnnotSentenceNum(f, mention)
                prev_tile = reconcile.getAnnotTile(f, mention)

                if mention.getATTR("is_pronoun"):
                    prev_type = "PRO"
                elif mention.getATTR("is_proper"):
                    prev_type = "PRP"
                else:
                    prev_type = "NOM"

    if options.duncan_files is not None:
        #add in the duncan statistics
        duncan_nominal_stats.add_in_duncan(options.duncan_files, text2nominal)

    #output a human/machine format
    if options.pprint:
        output_to_human(text2nominal)

    if options.pickle:
        pickle.dump(noun2antecedents, open("promed-gold-stats.p", "wb"))

    if options.write_stats:
        output_to_file(options.outfile, text2nominal)
