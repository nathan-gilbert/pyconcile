#!/usr/bin/python
# File Name : vp_accuracy.py
# Purpose :
# Creation Date : 10-21-2013
# Last Modified : Wed 29 Jan 2014 03:26:04 PM MST
# Created By : Nathan Gilbert
#
import sys
import string

import qp_utils
from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-list> <vp-list> [-hobbs|-rap|-rec|-sieve|-baseline]" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"), fileList.readlines()))

    QPs = []
    with open(sys.argv[2], 'r') as vpList:
        QPs.extend(map(string.strip, filter(lambda x : not x.startswith("#"),
            vpList.readlines())))

    if sys.argv[1].find("ace") > -1:
        ACE = True
        qp_utils.set_dataset("ACE")
    else:
        ACE = False

    if sys.argv[1].find("muc4") > -1:
        MUC4 = True
        qp_utils.set_dataset("MUC4")
    else:
        MUC4 = False

    if sys.argv[1].find("muc6") > -1:
        MUC6 = True
        qp_utils.set_dataset("MUC6")
    else:
        MUC6 = False

    if sys.argv[1].find("muc7") > -1:
        MUC7 = True
        qp_utils.set_dataset("MUC7")
    else:
        MUC7 = False

    if sys.argv[1].find("promed") > -1:
        PROMED = True
        qp_utils.set_dataset("PROMED")
    else:
        PROMED = False

    total_scores = {"vps_guessed" : 0,
                    "vps_correct" : 0
                    }

    RESPONSE_TYPE = ""
    for f in files:
        f=f.strip()
        print "Working on file: {0}".format(f)
        gold_chains = reconcile.getGoldChains(f)
        pos = reconcile.getPOS(f)
        pairs = []
        if "-hobbs" in sys.argv:
            RESPONSE_TYPE = "Hobbs"
            #read in the hobbs annotations
            hobbs_pairs = reconcile.getProResPairs(f, "hobbs")
            for pair in hobbs_pairs:
                tags = pos.getSubset(pair[1].getStart(), pair[1].getEnd())
                text = utils.textClean(pair[1].getText()).lower()
                ana_head = qp_utils.getHead2(text, tags)
                print "{0:40} => {1}".format(text, ana_head)
                if ana_head in QPs:
                    pairs.append(pair)

                #if pair[1].getText().lower() not in data.ALL_PRONOUNS:
                #    pairs.append(pair)

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
                ana_head = qp_utils.getHead2(utils.textClean(pair[1].getText())).lower()
                if ana_head in QPs:
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
                ana_head = qp_utils.getHead2(utils.textClean(pair[1].getText())).lower()
                if ana_head in QPs:
                    pairs.append(pair)
                #if pair[1].getText().lower() not in data.ALL_PRONOUNS:
                #    pairs.append(pair)
        elif "-rap" in sys.argv:
            RESPONSE_TYPE = "RAP"
            #read in the lappin/leass annotations
            rap_pairs = reconcile.getProResPairs(f, "rap")
            for pair in rap_pairs:
                tags = pos.getSubset(pair[1].getStart(), pair[1].getEnd())
                text = utils.textClean(pair[1].getText()).lower()
                ana_head = qp_utils.getHead2(text, tags)
                if ana_head in QPs:
                    pairs.append(pair)

                #if pair[1].getText().lower() not in data.ALL_PRONOUNS:
                #    pairs.append(pair)
        elif "-baseline" in sys.argv:
            RESPONSE_TYPE = "Baseline"
            baseline_pairs = reconcile.getFauxPairs(f, "features.goldnps/predictions.Baseline.byte_dist")
            for pair in baseline_pairs:
                tags = pos.getSubset(pair[1].getStart(), pair[1].getEnd())
                text = utils.textClean(pair[1].getText()).lower()
                ana_head = qp_utils.getHead2(text, tags)
                if ana_head in QPs:
                    pairs.append(pair)
        else:
            print "Please select response type."
            sys.exit(1)

        labeled_annots = reconcile.labelCorrectPairs(gold_chains, pairs)
        for pair in labeled_annots:
            total_scores["vps_guessed"] += 1
            if pair[2]:
                print pair[0].ppprint() + " <- " + pair[1].ppprint()
                total_scores["vps_correct"] += 1
            else:
                print pair[0].ppprint() + " <- " + pair[1].ppprint() + "*"

    print "="*72
    print "{0} accuracy".format(RESPONSE_TYPE)
    try:
        result = total_scores["vps_correct" ] / float(total_scores["vps_guessed"])
        print "Total: {0} / {1} = {2:0.2f}".format(total_scores["vps_correct"],
                total_scores["vps_guessed"], result)
    except:
        result = 0.0
        print "Total: {0} / {1} = {2:0.2f}".format(total_scores["vps_correct"],
                total_scores["vps_guessed"], result)

