#!/usr/bin/python
# File Name : duncan-accuracy.py
# Purpose :
# Creation Date : 03-22-2013
# Last Modified : Fri 22 Mar 2013 02:53:58 PM MDT
# Created By : Nathan Gilbert
#
import sys
import subprocess
import pickle
import operator

import lkb_lib
from pyconcile.bar import ProgressBar

def getHead(text):
    p1 = subprocess.Popen(["/usr/bin/java", "ReconcileStringFormat",
        "\"{0}\"".format(text)], stdout=subprocess.PIPE)
    return p1.stdout.read().replace("\"","").strip()

def check(pair, lkb, cache):
    if pair[0] in list(lkb.keys()):
        if pair[1] not in list(cache.keys()):
            anaphor_head = getHead(pair[1])
            cache[pair[1]] = anaphor_head
        else:
            anaphor_head = cache[pair[1]]

        antecedents = lkb[pair[0]].getAntecedentCounts()
        for antecedent in list(antecedents.keys()):
            if antecedent not in list(cache.keys()):
                antecedent_head = getHead(antecedent)
                cache[antecedent] = antecedent_head
            else:
                antecedent_head = cache[antecedent]

            if (antecedent_head == anaphor_head):
                if pair[2]:
                    return "CORRECT"
                else:
                    return "INCORRECT"

    if pair[1] in list(lkb.keys()):
        if pair[0] not in list(cache.keys()):
            anaphor_head = getHead(pair[0])
            cache[pair[0]] = anaphor_head
        else:
            anaphor_head = cache[pair[0]]
        antecedents = lkb[pair[1]].getAntecedentCounts()
        for antecedent in antecedents:
            if antecedent not in list(cache.keys()):
                antecedent_head = getHead(antecedent)
                cache[antecedent] = antecedent_head
            else:
                antecedent_head = cache[antecedent]

            if (antecedent_head == anaphor_head):
                if pair[2]:
                    return "CORRECT"
                else:
                    return "INCORRECT"

    #means that neither the antecedent nor anaphor were found in the lkb
    if pair[2]:
        return "NOTFOUND+"
    else:
        return "NOTFOUND-"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <duncan-lkb> <gold-lkb> <pair-file>" % (sys.argv[0]))
        sys.exit(1)

    duncan_lkb = lkb_lib.read_in_lkb(sys.argv[1])
    gold_lkb = lkb_lib.read_in_lkb(sys.argv[2])

    pair_lines =[]
    with open(sys.argv[3], 'r') as pairList:
        pair_lines.extend(pairList.readlines())

    pairs = []
    for line in pair_lines:
        if line.startswith("#"):
            continue
        if line.find("FOLD") > -1:
            continue
        line=line.strip()
        line=line.replace("Pair: ", "")
        tokens = line.split(" <= ")
        antecedent = tokens[0].strip()
        anaphor = tokens[1].strip()
        if anaphor.find("$!$") > -1:
            correct = True
            anaphor = anaphor.replace("$!$", "").strip()
        else:
            correct = False
        pair = (antecedent, anaphor, correct)
        pairs.append(pair)

    #cycle over the pairs and determine their accuracy.
    try:
        cache = pickle.load(open("cache.p", "rb"))
    except:
        cache = {}

    statistics = {
            "DUNCAN_CORRECT" : 0, "DUNCAN_INCORRECT" : 0,
            "GOLD_CORRECT" : 0, "GOLD_INCORRECT" : 0,
            "BOTH_CORRECT" : 0, "BOTH_INCORRECT" : 0,
            "DUNCAN_NOTFOUND": 0, "GOLD_NOTFOUND" : 0,
            "BOTH_NOTFOUND+" : 0, "BOTH_NOTFOUND-": 0
            }

    total_pairs = 0
    sys.stdout.flush()
    sys.stdout.write("\r")
    prog = ProgressBar(len(pairs))
    sys.stdout.write("\r")
    #sys.stdout.write("\r \r\n")
    duncan_correct_pairs = {}
    duncan_incorrect_pairs = {}
    missing = {}
    for pair in pairs:
        #print "Working on pair: {0}/{1}".format(total_pairs, len(pairs))
        prog.update_time(total_pairs)
        sys.stdout.write("\r%s" % (str(prog)))
        sys.stdout.flush()
        total_pairs += 1
        duncan_result = check(pair, duncan_lkb, cache)
        gold_result = check(pair, gold_lkb, cache)

        #NOTE: how many pairs do both lkbs get correct? -- this is useful, but
        #ultimately we don't care how many they *both* get.
        if duncan_result == "CORRECT" and gold_result == "CORRECT":
            statistics["BOTH_CORRECT"] = statistics["BOTH_CORRECT"] + 1
        #NOTE: how many pairs do we get with duncan that we don't get from the
        #gold?
        if (duncan_result == "CORRECT") and gold_result.startswith("NOTFOUND"):
            statistics["DUNCAN_CORRECT"] = statistics["DUNCAN_CORRECT"] + 1

        if (duncan_result == "INCORRECT"):
            statistics["DUNCAN_INCORRECT"] = statistics["DUNCAN_INCORRECT"] + 1
        if (gold_result == "INCORRECT"):
            statistics["GOLD_INCORRECT"] = statistics["GOLD_INCORRECT"] + 1

        if (duncan_result == "CORRECT") and gold_result in ("CORRECT", "NOTFOUND+", "NOTFOUND-"):
            duncan_correct_pairs[pair[0]+":"+pair[1]] = duncan_correct_pairs.get(pair[0]+":"+pair[1], 0) + 1

        #NOTE: the number of times that the gold is correct and we didn't have 
        #anything in Duncan
        if (gold_result == "CORRECT") and duncan_result.startswith("NOTFOUND"):
            statistics["GOLD_CORRECT"] = statistics["GOLD_CORRECT"] + 1

        if (duncan_result == "INCORRECT") and gold_result in ("CORRECT", "NOTFOUND+", "NOTFOUND-"):
            duncan_incorrect_pairs[pair[0]+":"+pair[1]] = duncan_incorrect_pairs.get(pair[0]+":"+pair[1], 0) + 1

        #NOTE: when both sources are incorrect
        if gold_result == "INCORRECT" and duncan_result == "INCORRECT":
            statistics["BOTH_INCORRECT"] = statistics["BOTH_INCORRECT"] + 1

        #NOTE: when the pair is not found by either (often a good thing, for
        #pairs that are not-coreferent
        if gold_result == "NOTFOUND+" and duncan_result == "NOTFOUND+":
            statistics["BOTH_NOTFOUND+"] = statistics["BOTH_NOTFOUND+"] + 1
            missing[pair[0]+":"+pair[1]] = missing.get(pair[0]+":"+pair[1], 0) + 1

        if gold_result == "NOTFOUND-" and duncan_result == "NOTFOUND-":
            statistics["BOTH_NOTFOUND-"] = statistics["BOTH_NOTFOUND-"] + 1

    #print "Correct: {0}".format(statistics["CORRECT"])
    #print "Incorrect: {0}".format(statistics["INCORRECT"])
    #print "Not Found: {0}".format(statistics["NOTFOUND"])
    sys.stdout.write("\r \r\n")
    sorted_keys = sorted(statistics.keys())
    for key in sorted_keys:
        print("{0:25} : {1}".format(key, statistics[key]))

    sorted_keys = sorted(iter(duncan_correct_pairs.items()),
            key=operator.itemgetter(1), reverse=True)
    print("#"*15 + "CORRECT" + "#"*15)
    for key_value in sorted_keys:
        print("{0:30} : {1}".format(key_value[0], key_value[1]))

    print("#"*15 + "INCORRECT" + "#"*15)
    sorted_keys = sorted(iter(duncan_incorrect_pairs.items()),
            key=operator.itemgetter(1), reverse=True)
    for key_value in sorted_keys:
        print("{0:30} : {1}".format(key_value[0], key_value[1]))

    print("#"*15 + "MISSING" + "#"*15)
    sorted_keys = sorted(iter(missing.items()),
            key=operator.itemgetter(1), reverse=True)
    for key_value in sorted_keys:
        print("{0:30} : {1}".format(key_value[0], key_value[1]))

    pickle.dump(cache, open("cache.p", "wb"))

