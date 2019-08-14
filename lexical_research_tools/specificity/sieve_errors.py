#!/usr/bin/python
# File Name : sieve_errors.py
# Purpose : Analyze the types of errors that the Sieve is making.
# Creation Date : 11-20-2013
# Last Modified : Wed 29 Jan 2014 09:33:28 PM MST
# Created By : Nathan Gilbert
#
import sys
import collections

from pyconcile import reconcile
from pyconcile import utils
import specificity_utils

#DONE: cases where the correct antecedent is further than 5 sentences away
#TODO: cases where there is a closer "same-semantic-type" than the true
#      antecedent
#TODO: cases where other heuristics are stopping the resolution -- may need to
#      look at other output
#TODO: grab cases where no resolution is made

class Noun:
    def __init__(self, h):
        self.head     = h
        self.instances = {} #doc:start:end -> text
        self.antecedents = {} #doc:start:end -> ante_text
        self.labels    = {} #doc:start:end -> True/False
        self.true_antecedent_distances = {} #doc:start:end -> sentence distance
                                            # of closest true antecedent
        self.resp_antecedent_distances = {} #doc:start:end -> sentence distance
                                            #of response antencedent
        self.incorrect_ante_sc         = {} #doc:start:end -> #

    def greaterThan5(self):
        five = 0
        for key in list(self.true_antecedent_distances.keys()):
            if self.true_antecedent_distances[key] > 4:
                five += 1
        return five

    def baseAntencedent(self):
        ba = 0
        for key in list(self.true_antecedent_distances.keys()):
            if self.true_antecedent_distances[key] < 0 :
                ba += 1
        return ba

    def count(self):
        return len(list(self.instances.keys()))

    def num_correct(self):
        return len([x for x in list(self.labels.values()) if x == True])

def closest_antecedent(gold_chains, mention):
    """returns the closest antecedent in the text. if base antecedent,
    returns None"""
    #find this mention in gold chains
    for key in list(gold_chains.keys()):
        prev = None
        for other in gold_chains[key]:
            if mention == other:
                return prev
            else:
                prev = other
    return None

def getAnnotSentenceNum(sentences, annot):
    """return the integer of the sentence the annot is found in."""
    if annot is None:
        return -1

    i = 0
    for s in sentences:
        if s.contains(annot):
            return i
        i += 1
    return -1

def getAnnotSemanticClass(nes, annot):
    if annot is None:
        return None
    return nes.getAnnotBySpan(annot.getStart(), annot.getEnd())["NE_CLASS"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    FAUX_PRONOUNS = []
    with open(sys.argv[2], 'r') as fauxFile:
        for line in fauxFile:
            if line.startswith("#"):
                continue
            line=line.strip()
            FAUX_PRONOUNS.append(line)

    PREDICTIONS = "features.goldnps/predictions.StanfordSieve.all_commons/"
    #PREDICTIONS = "features.goldnps/predictions.StanfordSieve.bare_definites/"

    files = []
    tracked_nouns = {} #head -> Noun instance
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    overall_sc_errors = {}
    for f in files:
        f=f.strip()
        #print "Working on file: {0}".format(f)

        #get the gold chains
        gold_chains = reconcile.getGoldChains(f)
        gold_nes = reconcile.getGoldNEs(f)

        #get faux pronouns
        try:
            faux_pronoun_pairs = reconcile.getFauxPairs(f, PREDICTIONS)
        except:
            #then one was not created for this document (ACE04-33 is one.)
            continue

        #get the sentences 
        sentences = reconcile.getSentences(f)

        #remove the pairs we don't care about
        tracked_pairs = []
        for pair in faux_pronoun_pairs:
            ana_head = specificity_utils.getHead(pair[1].getText()).lower()
            if ana_head in FAUX_PRONOUNS:
                if ana_head not in list(tracked_nouns.keys()):
                    tracked_nouns[ana_head] = Noun(ana_head)
                tracked_pairs.append(pair)

        #label the correct or incorrect pairs
        labeled_faux_pairs = reconcile.labelCorrectPairs(gold_chains,
                tracked_pairs)

        for lpair in labeled_faux_pairs:
            ana_head = specificity_utils.getHead(lpair[1].getText()).lower()
            key = "{0}:{1}:{2}".format(f, lpair[1].getStart(),
                    lpair[1].getEnd())

            tracked_nouns[ana_head].instances[key] = utils.textClean(lpair[1].getText())
            tracked_nouns[ana_head].antecedents[key] = utils.textClean(lpair[0].getText())
            tracked_nouns[ana_head].labels[key] = lpair[2]

            #this is an incorrect antecedent
            if not lpair[2]:
                closest_true_antecedent = closest_antecedent(gold_chains,
                        lpair[1])

                #deals with sentence distance
                resp_ant_sent = getAnnotSentenceNum(sentences, lpair[1])
                true_ant_sent = getAnnotSentenceNum(sentences, closest_true_antecedent)
                ana_sent = getAnnotSentenceNum(sentences, lpair[1])

                if closest_true_antecedent is not None:
                    true_dist = ana_sent - true_ant_sent
                else:
                    true_dist = -1
                resp_dist = ana_sent - resp_ant_sent

                tracked_nouns[ana_head].true_antecedent_distances[key] = true_dist
                tracked_nouns[ana_head].resp_antecedent_distances[key] = resp_dist

                #deals with semantic issues
                true_ant_sc = getAnnotSemanticClass(gold_nes,closest_true_antecedent)
                ana_sc = getAnnotSemanticClass(gold_nes, lpair[1])

                if (closest_true_antecedent is not None) and (true_ant_sc != ana_sc):
                    #this case captures when the true antecedent has a
                    #different semantic class than the anaphor
                    tracked_nouns[ana_head].incorrect_ante_sc[key] = true_ant_sc
                else:
                    #this captures the semantic class that caused  the
                    #incorrect resolution
                    overall_sc_errors[ana_sc] = overall_sc_errors.get(ana_sc,0) + 1

    stn = sorted(list(tracked_nouns.values()), key=lambda x : x.count(), reverse=True)
    for tn in stn:
        print("Head: {0}".format(tn.head))
        print("\tresolutions: {0} / {1} = {2:.2f}".format(tn.num_correct(), tn.count(),
                float(tn.num_correct()) / tn.count()))
        print("\t>5 antecedents: {0}".format(tn.greaterThan5()))
        print("\tno antecedents: {0}".format(tn.baseAntencedent()))
        print("\tincorrect sem: {0}".format(len(list(tn.incorrect_ante_sc.keys()))))

        incorrect = []
        for ant in list(tn.antecedents.keys()):
            if not tn.labels[ant]:
                incorrect.append(tn.antecedents[ant])
        most_common_incorrect = collections.Counter(incorrect).most_common(5)

        print("\ttop 5 incorrect: {0}".format(", ".join([x[0] for x in most_common_incorrect])))
        print("="*72)

    total_sc_errors = sum(overall_sc_errors.values())
    for key in list(overall_sc_errors.keys()):
        print("{0:15} : {1:3} : {2:.2f}".format(key, overall_sc_errors[key],
                float(overall_sc_errors[key]) / total_sc_errors))

