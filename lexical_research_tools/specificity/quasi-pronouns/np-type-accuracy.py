#!/usr/bin/python
# File Name : np-type-accuracy.py
# Purpose :
# Creation Date : 01-15-2014
# Last Modified : Wed 29 Jan 2014 09:36:29 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import data
import qp_utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    results = {
            "PROPER" : { "c" : 0, "i" : 0, "n" : 0},
            "COMMON" : { "c" : 0, "i" : 0, "n" : 0},
            "PRONOUN1" : { "c" : 0, "i" : 0, "n" : 0},
            "PRONOUN3g" : { "c" : 0, "i" : 0, "n" : 0},
            "PRONOUN3n" : { "c" : 0, "i" : 0, "n" : 0}
            }

    if sys.argv[1].find("muc6") > -1:
        qp_utils.set_dataset("MUC6")
        PREDICTIONS = "features.goldnps/predictions.DecisionTree.muc6_DecisionTree_goldnps"
    elif sys.argv[1].find("muc7") > -1:
        qp_utils.set_dataset("MUC7")
        PREDICTIONS = "features.goldnps/predictions.DecisionTree.muc7_DecisionTree_goldnps"
    elif sys.argv[1].find("muc4") > -1:
        qp_utils.set_dataset("MUC4")
        PREDICTIONS = "features.goldnps-#/predictions.DecisionTree.muc4_DecisionTree_goldnps-#"
    elif sys.argv[1].find("promed") > -1:
        qp_utils.set_dataset("PROMED")
        PREDICTIONS = "features.goldnps-#/predictions.DecisionTree.promed_DecisionTree_goldnps-#"

    if "+s" in sys.argv:
        PREDICTIONS = "features.goldnps/predictions.StanfordSieve.default"

    #grab the pairwise results from each file
    total_nps = 0

    #TODO break down pronouns into three groups
    total_proper = 0
    total_common = 0
    total_pronoun1 = 0
    total_pronoun3g = 0
    total_pronoun3n = 0

    uniq_proper = 0
    uniq_common  = 0
    uniq_pronoun1 = 0
    uniq_pronoun3g = 0
    uniq_pronoun3n = 0

    nouns_not_found = []
    nouns_incorrect = []

    for f in files:
        f=f.strip()
        if f.startswith("#") : continue

        pos = reconcile.getPOS(f)
        gold_chains = reconcile.getGoldChains(f)

        #getting promed or muc4 fold scores
        if PREDICTIONS.find("promed") > -1 or PREDICTIONS.find("muc4") > -1:
            try:
                response_pairs = reconcile.getResponsePairs(f,
                        PREDICTIONS.replace("#", "0"))
            except:
                try:
                    response_pairs = reconcile.getResponsePairs(f,
                        PREDICTIONS.replace("#", "1"))
                except:
                    try:
                        response_pairs = reconcile.getResponsePairs(f,
                            PREDICTIONS.replace("#", "2"))
                    except:
                        try:
                            response_pairs = reconcile.getResponsePairs(f,
                                PREDICTIONS.replace("#", "3"))
                        except:
                            response_pairs = reconcile.getResponsePairs(f,
                                PREDICTIONS.replace("#", "4"))
        else:
            response_pairs = reconcile.getResponsePairs(f, PREDICTIONS)

        #cycle trough labeled pairs and see which ones do not have an
        #antecedent and also do not start a chain.
        no_antecedent_attempts = []
        for key in list(gold_chains.keys()):
            #skip the first mention because it's not supposed to have an
            #antecedent
            total_nps += len(gold_chains[key])
            for mention in gold_chains[key][1:]:
                found = False
                for pair in response_pairs:
                    #if the anaphor is this mention, then the system attempted
                    #a resolution
                    if pair[1] == mention:
                        if qp_utils.isNominal(pair[1], pos):
                            print("{0}".format(pair[1].getText()))
                            uniq_common += 1
                        elif qp_utils.isProper(pair[1], pos):
                            uniq_proper += 1
                        elif qp_utils.isPronoun(pair[1]):
                            if pair[1].getText().lower() in data.FIRST_PER:
                                uniq_pronoun1 += 1
                            elif pair[1].getText().lower() in data.THIRD_PERSON:
                                uniq_pronoun3g += 1
                            elif pair[1].getText().lower() in ("it", "they", "them"):
                                uniq_pronoun3n += 1
                        #else:
                        #    print "{0}".format(pair[1].getText().replace("\n", " "))
                        found = True
                        break
                if not found:
                    no_antecedent_attempts.append(mention)

        for mention in no_antecedent_attempts:
            if qp_utils.isNominal(mention, pos):
                uniq_common += 1
                results["COMMON"]["n"] = results["COMMON"]["n"] + 1
                nouns_not_found.append(mention.ppprint())
            elif qp_utils.isProper(mention, pos):
                uniq_proper += 1
                results["PROPER"]["n"] = results["PROPER"]["n"] + 1
            elif qp_utils.isPronoun(mention):
                if mention.getText().lower() in data.FIRST_PER:
                    results["PRONOUN1"]["n"] = results["PRONOUN1"]["n"] + 1
                    uniq_pronoun1 += 1
                elif mention.getText().lower() in data.THIRD_PERSON:
                    results["PRONOUN3g"]["n"] = results["PRONOUN3g"]["n"] + 1
                    uniq_pronoun3g += 1
                elif mention.getText().lower() in ("it", "they", "them"):
                    results["PRONOUN3n"]["n"] = results["PRONOUN3n"]["n"] + 1
                    uniq_pronoun3n += 1
            else:
                #print "{0}".format(mention.getText().replace("\n", " "))
                uniq_common += 1
                results["COMMON"]["n"] = results["COMMON"]["n"] + 1

        labeled_annots = reconcile.labelCorrectPairs(gold_chains, response_pairs)
        already_counted = []
        for pair in labeled_annots:
            #is it correct? 
            #is it incorrect? 
            #find the anaphor type
            if qp_utils.isProper(pair[1], pos):
                total_proper += 1
                if pair[2]:
                    results["PROPER"]["c"] = results["PROPER"]["c"] + 1
                else:
                    results["PROPER"]["i"] = results["PROPER"]["i"] + 1
                    nouns_incorrect.append(pair[1].ppprint())
            elif qp_utils.isNominal(pair[1], pos):
                total_common += 1
                if pair[2]:
                    results["COMMON"]["c"] = results["COMMON"]["c"] + 1
                else:
                    results["COMMON"]["i"] = results["COMMON"]["i"] + 1
            elif qp_utils.isPronoun(pair[1]):
                if pair[2]:
                    if pair[1].getText().lower() in data.FIRST_PER:
                        total_pronoun1 += 1
                        results["PRONOUN1"]["c"] = results["PRONOUN1"]["c"] + 1
                    elif pair[1].getText().lower() in data.THIRD_PERSON:
                        total_pronoun3g += 1
                        results["PRONOUN3g"]["c"] = results["PRONOUN3g"]["c"] + 1
                    elif pair[1].getText().lower() in ("it", "they", "them"):
                        total_pronoun3n += 1
                        results["PRONOUN3n"]["c"] = results["PRONOUN3n"]["c"] + 1
                else:
                    if pair[1].getText().lower() in data.FIRST_PER:
                        total_pronoun1 += 1
                        results["PRONOUN1"]["i"] = results["PRONOUN1"]["i"] + 1
                    elif pair[1].getText().lower() in data.THIRD_PERSON:
                        total_pronoun3g += 1
                        results["PRONOUN3g"]["i"] = results["PRONOUN3g"]["i"] + 1
                    elif pair[1].getText().lower() in ("it", "they", "them"):
                        total_pronoun3n += 1
                        results["PRONOUN3n"]["i"] = results["PRONOUN3n"]["i"] + 1
            else:
                #print "Couldn't find NP type: {0}".format(pair[1].ppprint())
                total_proper += 1
                if pair[2]:
                    results["COMMON"]["c"] = results["COMMON"]["c"] + 1
                else:
                    results["COMMON"]["i"] = results["COMMON"]["i"] + 1

    print()
    print("TOTAL NPs: {0}".format(total_nps))

    try:
        c_p = float(results["PROPER"]["c"]) / total_proper
    except:
        c_p = 0.0
    try:
        i_p = float(results["PROPER"]["i"]) / total_proper
    except:
        i_p = 0.0
    try:
        n_p = float(results["PROPER"]["n"]) / uniq_proper
    except:
        n_p = 0.0
    print("PROPER    {0:3.2f} {1:3.2f} {2:3.2f}".format(c_p, i_p, n_p))

    try:
        c_n = float(results["COMMON"]["c"]) / total_common
    except:
        c_n = 0.0
    try:
        i_n = float(results["COMMON"]["i"]) / total_common
    except:
        i_n = 0.0
    try:
        n_n = float(results["COMMON"]["n"]) / uniq_common
    except:
        n_n = 0.0
    print("COMMON    {0:3.2f} {1:3.2f} {2:3.2f}".format(c_n, i_n, n_n))

    try:
        c_pr = float(results["PRONOUN1"]["c"]) / total_pronoun1
    except:
        c_pr = 0.0
    try:
        i_pr = float(results["PRONOUN1"]["i"]) / total_pronoun1
    except:
        i_pr = 0.0
    try:
        n_pr = float(results["PRONOUN1"]["n"]) / uniq_pronoun1
    except:
        n_pr = 0.0
    print("PRONOUN1  {0:3.2f} {1:3.2f} {2:3.2f}".format(c_pr, i_pr, n_pr))

    try:
        c_pr = float(results["PRONOUN3g"]["c"]) / total_pronoun3g
    except:
        c_pr = 0.0
    try:
        i_pr = float(results["PRONOUN3g"]["i"]) / total_pronoun3g
    except:
        i_pr = 0.0
    try:
        n_pr = float(results["PRONOUN3g"]["n"]) / uniq_pronoun3g
    except:
        n_pr = 0.0
    print("PRONOUN3g {0:3.2f} {1:3.2f} {2:3.2f}".format(c_pr, i_pr, n_pr))

    try:
        c_pr = float(results["PRONOUN3n"]["c"]) / total_pronoun3n
    except:
        c_pr = 0.0
    try:
        i_pr = float(results["PRONOUN3n"]["i"]) / total_pronoun3n
    except:
        i_pr = 0.0
    try:
        n_pr = float(results["PRONOUN3n"]["n"]) / uniq_pronoun3n
    except:
        n_pr = 0.0
    print("PRONOUN3n {0:3.2f} {1:3.2f} {2:3.2f}".format(c_pr, i_pr, n_pr))

    #for noun in nouns_not_found:
    #    print noun
    #print "="*70
    #for noun in nouns_incorrect:
    #    print noun
