#!/usr/bin/python
# File Name : pronoun_accuracy.py
# Purpose : Measure the accuracy of pronoun resolutions by a system
# Creation Date : 09-12-2013
# Last Modified : Wed 22 Jan 2014 04:21:34 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

def getReconcilePairs(datadir):
    predictions = "features.goldnps/predictions.DecisionTree.muc6_DecisionTree_goldnps"
    response_pairs = reconcile.getResponsePairs(datadir, predictions)
    pronouns = ("he", "him", "she", "her", "it", "its", "they", "them")
    pairs = []
    for pair in response_pairs:
        if pair[1].getText().lower() in pronouns:
            pairs.append(pair)
    return pairs

def getSievePairs(datadir):
    predictions = "features.goldnps/predictions.StanfordSieve.default"
    response_pairs = reconcile.getResponsePairs(datadir, predictions)
    pronouns = ("he", "him", "she", "her", "it", "its", "they", "them")
    pairs = []
    for pair in response_pairs:
        if pair[0] is None or pair[1] is None:
            continue

        if pair[1].getText().lower() in pronouns:
            pairs.append(pair)
    return pairs

def getAnaphorType(anaphor):
    if anaphor.getText().lower() in ("he", "him", "she"):
        return "third_person"
    elif anaphor.getText().lower() in ("it"):
        return "it"
    elif anaphor.getText().lower() in ("them", "they"):
        return "plural"
    else:
        #print anaphor.getText().lower()
        return "unk"

    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-list> [-hobbs|-rap|-rec|-sieve|-baseline]" % (sys.argv[0])
        sys.exit(1)

    pronoun_types = {
            "third_person" : ["he","him","she", "her"],
            "it"           : ["it", "its"],
            "plural"       : ["they", "them"]
            }

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"), fileList.readlines()))

    total_scores = { "third_person_correct" : 0,
                     "third_person_guessed" : 0,
                     "it_correct"           : 0,
                     "it_guessed"           : 0,
                     "plural_correct"       : 0,
                     "plural_guessed"       : 0,
                     }
    for f in files:
        f=f.strip()
        print "Working on file: {0}".format(f)
        gold_chains = reconcile.getGoldChains(f)

        if "-rap" in sys.argv:
            #read in the hobbs annotations
            response_pairs = reconcile.getProResPairs(f, "rap")
        elif "-hobbs" in sys.argv:
            response_pairs = reconcile.getProResPairs(f, "hobbs")
        elif "-rec" in sys.argv:
            response_pairs = getReconcilePairs(f)
        elif "-sieve" in sys.argv:
            response_pairs = getSievePairs(f)
        elif "-baseline" in sys.argv:
            response_pairs = reconcile.getMentionDistancePronounPairs(f,
                    "features.goldnps/predictions.Baseline.byte_dist")
        else:
            print "Select response type."
            sys.exit(1)

        labeled_annots = reconcile.labelCorrectPairs(gold_chains, response_pairs)
        for pair in labeled_annots:
            #find out what the anaphor is
            anaphor_type = getAnaphorType(pair[1])
            if anaphor_type == "unk": continue
            total_scores[anaphor_type+"_guessed"] += 1
            if pair[2]:
                print pair[0].ppprint() + " <- " + pair[1].ppprint()
                total_scores[anaphor_type+"_correct"] += 1
            else:
                print pair[0].ppprint() + " <- " + pair[1].ppprint() + "*"


    print "="*72
    try:
        result = total_scores["third_person_correct"] / float(total_scores["third_person_guessed"])
    except:
        result = 0
    print "Third Person stats: {0} / {1} = {2:0.2f}".format(
            total_scores["third_person_correct"],
            total_scores["third_person_guessed"],
            result)
    try:
        result = total_scores["it_correct"] / float(total_scores["it_guessed"])
    except:
        result = 0
    print "IT stats: {0} / {1} = {2:0.2f}".format(
            total_scores["it_correct"],
            total_scores["it_guessed"],
            result)
    try:
        result = total_scores["plural_correct"] / float(total_scores["plural_guessed"])
    except:
        result = 0
    print "Plural stats: {0} / {1} = {2:0.2f}".format(
            total_scores["plural_correct"],
            total_scores["plural_guessed"],
            result)
    try:
        numerator = total_scores["plural_correct"] + total_scores["it_correct"] + total_scores["third_person_correct"]
        denom = total_scores["plural_guessed"] + total_scores["it_guessed"] + total_scores["third_person_guessed"]
        result = numerator / float(denom)
    except:
        result = 0
    print "Total: {0} / {1} = {2:0.2f}".format(
            numerator,
            denom,
            result)
