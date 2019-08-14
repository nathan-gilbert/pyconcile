#!/usr/bin/python
# File Name : vp_accuracy.py
# Purpose :
# Creation Date : 10-21-2013
# Last Modified : Tue 12 Nov 2013 04:31:04 PM MST
# Created By : Nathan Gilbert
#
import sys
import string

import specificity_utils
from pyconcile import reconcile
from pyconcile import utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list> <vp-list> [-hobbs|-rap|-rec|-sieve]" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    VPs = []
    with open(sys.argv[2], 'r') as vpList:
        VPs.extend(list(map(string.strip, [x for x in vpList.readlines() if not x.startswith("#")])))

    total_scores = {"vps_guessed" : 0,
                    "vps_correct" : 0
                    }

    RESPONSE_TYPE = ""
    for f in files:
        f=f.strip()
        print("Working on file: {0}".format(f))
        gold_chains = reconcile.getGoldChains(f)
        pairs = []
        if "-hobbs" in sys.argv:
            RESPONSE_TYPE = "Hobbs"
            #read in the hobbs annotations
            hobbs_pairs = reconcile.getProResPairs(f, "hobbs")
            for pair in hobbs_pairs:
                ana_head = specificity_utils.getHead(utils.textClean(pair[1].getText())).lower()
                if ana_head in VPs:
                    pairs.append(pair)
        elif "-rec" in sys.argv:
            #TODO if we choose this route then there needs to be some mods
            #since each vp can be resolved multiple times.
            # 1. only count the closest antecedent?
            # 2. don't count string matches?
            # 3. look at what is in the "pro_antes" property (that gives us the
            # Cogniac decision.
            # 4. take the average accuracy for each noun.
            RESPONSE_TYPE = "Reconcile"
            #predictions = "features.goldnps/predictions.DecisionTree.muc6_DecisionTree_goldnps"
            predictions = "features.goldnps-vps/predictions.DecisionTree.muc6_DecisionTree_goldnps-vps"
            pairs = reconcile.getResponsePairs(f, predictions)
            for pair in reconcile_pairs:
                ana_head = specificity_utils.getHead(utils.textClean(pair[1].getText())).lower()
                if ana_head in VPs:
                    pairs.append(pair)
        elif "-sieve" in sys.argv:
            RESPONSE_TYPE = "Sieve"
            #predictions  ="features.goldnp/predictions.StanfordSieve.default"
            #predictions = "features.goldnps/predictions.StanfordSieve.all_commons"
            predictions = "features.goldnps/predictions.StanfordSieve.bare_definites"
            response_pairs = reconcile.getResponsePairs(f, predictions)
            for pair in response_pairs:
                if pair[0] is None or pair[1] is None:
                    continue
                ana_head = specificity_utils.getHead(utils.textClean(pair[1].getText())).lower()
                if ana_head in VPs:
                    pairs.append(pair)
        elif "-rap" in sys.argv:
            RESPONSE_TYPE = "RAP"
            #read in the lappin/leass annotations
            rap_pairs = reconcile.getProResPairs(f, "rap")
            for pair in rap_pairs:
                ana_head = specificity_utils.getHead(utils.textClean(pair[1].getText())).lower()
                if ana_head in VPs:
                    pairs.append(pair)
        else:
            print("Please select response type.")
            sys.exit(1)

        labeled_annots = reconcile.labelCorrectPairs(gold_chains, pairs)
        for pair in labeled_annots:
            total_scores["vps_guessed"] += 1
            if pair[2]:
                print(pair[0].ppprint() + " <- " + pair[1].ppprint())
                total_scores["vps_correct"] += 1
            else:
                print(pair[0].ppprint() + " <- " + pair[1].ppprint() + "*")

    print("="*72)
    print("{0} accuracy".format(RESPONSE_TYPE))
    try:
        result = total_scores["vps_correct" ] / float(total_scores["vps_guessed"])
        print("Total: {0} / {1} = {2:0.2f}".format(total_scores["vps_correct"],
                total_scores["vps_guessed"], result))
    except:
        result = 0.0
        print("Total: {0} / {1} = {2:0.2f}".format(total_scores["vps_correct"],
                total_scores["vps_guessed"], result))

