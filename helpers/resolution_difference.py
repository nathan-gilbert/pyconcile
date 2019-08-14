#!/usr/bin/python
# File Name : resolution_difference.py
# Purpose :
# Creation Date : 09-15-2011
# Last Modified : Tue 18 Jun 2013 04:52:47 PM MDT
# Created By : Nathan Gilbert
#
import sys
from optparse import OptionParser

from pyconcile import reconcile

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file-list", help="filelist to use",
            action="store", dest="filelist", default="tmp.list")
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    base = "goldnps"
    second = "goldnps"

    #predictions
    predictions1="predictions.StanfordSieve.default"
    predictions2="predictions.StanfordSieve.virtualpronouns"

    files = []
    with open(options.filelist, 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"), map(lambda x :
            x.strip(), fileList.readlines())))

    total_new_correct_resolutions = 0
    total_new_incorrect_resolutions = 0
    for f in files:
        print "File: {0}".format(f)
        response1 = reconcile.getAllResponsePairs(f, "/features." + base + "/" + predictions1)
        response2 = reconcile.getAllResponsePairs(f, "/features." + second+"/" + predictions2)

        gold_chains = reconcile.getGoldChains(f)
        gold_response1 = reconcile.labelCorrectPairs(gold_chains,response1)
        gold_system1_pairs = {}
        for pair in gold_response1:
            key = "%s:%s" % (pair[0].getID(), pair[1].getID())
            gold_system1_pairs[key] = pair

        gold_system2_pairs = {}
        gold_response2 = reconcile.labelCorrectPairs(gold_chains,response2)
        for pair in gold_response2:
            key = "%s:%s" % (pair[0].getID(), pair[1].getID())
            gold_system2_pairs[key] = pair

        system1_pairs = {}
        system2_pairs = {}
        for pair in response1:
            if pair[2] > 0:
                key = "%s:%s" % (pair[0].getID(), pair[1].getID())
                system1_pairs[key] = pair

        for pair in response2:
            if pair[2] > 0:
                key = "%s:%s" % (pair[0].getID(), pair[1].getID())
                system2_pairs[key] = pair

        set1 = set(system1_pairs.keys())
        set2 = set(system2_pairs.keys())
        #print set1
        #print set2

        #these are the resolutions that the second system got that the first system
        #did not.
        diff = list(set2 - set1)
        correct    = []
        incorrect  = []
        for key in diff:
            antecedent = system2_pairs[key][0]
            anaphor = system2_pairs[key][1]
            gold =""
            if gold_system2_pairs[key][2]:
                gold = "(C)"
                correct.append("{0:3} {1:75} <- {2:75}".format(gold,
                    antecedent.ppprint(), anaphor.ppprint()))
            else:
                gold = "(X)"
                incorrect.append("{0:3} {1:75} <- {2:75}".format(gold,
                    antecedent.ppprint(), anaphor.ppprint()))

        total_new_correct_resolutions += len(correct)
        total_new_incorrect_resolutions += len(incorrect)
        for c in correct:
            print c
        for i in incorrect:
            print i

    total_new_resolutions = total_new_incorrect_resolutions + total_new_correct_resolutions
    print "New resolutions: {0}".format(total_new_resolutions)
    print "Correct: {0} / {1} = {2:.2f}".format(total_new_correct_resolutions,
            total_new_resolutions, float(total_new_correct_resolutions) / total_new_resolutions)
    print "Incorrect: {0} / {1} = {2:.2f}".format(total_new_incorrect_resolutions,
            total_new_resolutions, float(total_new_incorrect_resolutions) / total_new_resolutions)
