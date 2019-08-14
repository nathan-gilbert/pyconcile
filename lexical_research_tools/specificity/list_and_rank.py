#!/usr/bin/python
# File Name : list_and_rank.py
# Purpose :
# Creation Date : 10-30-2013
# Last Modified : Wed 11 Dec 2013 06:26:58 PM MST
# Created By : Nathan Gilbert
#
import sys
import string
import operator

import specificity_utils
from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data

class Noun:
    def __init__(self, h):
        self.head    = h
        self.count   = 1
        self.correct = 0
        self.docs    = []

    def updateCount(self):
        self.count += 1

    def updateCorrect(self):
        self.correct += 1

    def percent_correct(self):
        try:
            result = float(self.correct) / self.count
        except:
            result = 0.0
        return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list> [-hobbs|-rap|-rec|-sieve|-baseline]" % (sys.argv[0]))
        sys.exit(1)

    COUNT = 2
    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    total_scores = {"vps_guessed" : 0,
                    "vps_correct" : 0
                    }

    heads2nouns = {}
    VPs = []
    #if "-sieve" in sys.argv:
    #    with open(sys.argv[2], 'r') as vpList:
    #        VPs.extend(map(string.strip, filter(lambda x : not x.startswith("#"),
    #            vpList.readlines())))

    for f in files:
        f=f.strip()
        sys.stderr.write("Working on file: {0}\n".format(f))
        gold_chains = reconcile.getGoldChains(f)
        pairs = []

        if "-rap" in sys.argv:
            response_pairs = reconcile.getProResPairs(f, "rap")
        elif "-hobbs" in sys.argv:
            response_pairs = reconcile.getProResPairs(f, "hobbs")
        elif "-baseline" in sys.argv:
            predictions = "features.goldnps/predictions.Baseline.byte_dist"
            try:
                all_pairs = reconcile.getFauxPairs(f, predictions)
            except:
                continue

            response_pairs = []
            for pair in all_pairs:
                if pair[0] is None or pair[1] is None:
                    continue
                response_pairs.append(pair)

        elif "-sieve" in sys.argv:
            #predictions = "features.goldnps/predictions.StanfordSieve.bare_definites"
            #predictions = "features.goldnps/predictions.StanfordSieve.bare_definites_no_pre_cluster"
            predictions = "features.goldnps/predictions.StanfordSieve.bare_definites_no_pre_cluster_no_ace_annots"

            #in case there were no predictions in a file
            try:
                all_pairs = reconcile.getFauxPairs(f, predictions)
            except:
                continue

            response_pairs = []
            for pair in all_pairs:
                if pair[0] is None or pair[1] is None:
                    continue
                response_pairs.append(pair)

        for pair in response_pairs:
            ana_head = specificity_utils.getHead(utils.textClean(pair[1].getText())).lower().strip()
            #skip real pronouns
            if ana_head not in data.ALL_PRONOUNS:
                pairs.append(pair)
                if ana_head not in list(heads2nouns.keys()):
                    heads2nouns[ana_head] = Noun(ana_head)
                else:
                    heads2nouns[ana_head].updateCount()

        labeled_annots = reconcile.labelCorrectPairs(gold_chains, pairs)
        for pair in labeled_annots:
            total_scores["vps_guessed"] += 1
            ana_head = specificity_utils.getHead(utils.textClean(pair[1].getText())).lower().strip()
            if pair[2]:
                #correct pair
                #print pair[0].ppprint() + " <- " + pair[1].ppprint()
                total_scores["vps_correct"] += 1
                heads2nouns[ana_head].updateCorrect()
            #else:
                #incorrect pair
                #print pair[0].ppprint() + " <- " + pair[1].ppprint() + "*"


    #sort the dict by percentage correct
    #do not consider nouns that occurred less than 3 times.
    sorted_nouns = sorted(list(heads2nouns.values()), key=lambda x : x.count, reverse=True)
    sorted_nouns = sorted(sorted_nouns, key=lambda x : x.percent_correct(), reverse=True)

    for sn in sorted_nouns:
        if sn.count > COUNT:
            print("{0:.2f} : {1:3} : {2:3} : {3:15}".format(sn.percent_correct(), sn.correct, sn.count, sn.head))

    print("="*72)
    try:
        result = total_scores["vps_correct" ] / float(total_scores["vps_guessed"])
        print("Total: {0} / {1} = {2:0.2f}".format(total_scores["vps_correct"],
                total_scores["vps_guessed"], result))
    except:
        result = 0.0
        print("Total: {0} / {1} = {2:0.2f}".format(total_scores["vps_correct"],
                total_scores["vps_guessed"], result))
