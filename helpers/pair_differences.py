#!/usr/bin/python
# File Name : pair_differences.py
# Purpose : Checks the differences of the pairwise resolutions between separate
# Reconcile runs
# Creation Date : 04-07-2013
# Last Modified : Mon 08 Apr 2013 10:35:57 AM MDT
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    #base = "goldnps"
    base = "goldnps-WordPairBinary"
    #second = "goldnps-LexicoSemanticSundanceBinary"
    #second = "goldnps-SetSundance"
    #second = "goldnps-WordPairBinary"
    second = "goldnps-WordPairBinary-LexicoSemanticSundanceBinary"

    #predictions1="predictions.DecisionTree.muc6_DecisionTree_goldnps"
    predictions1="predictions.DecisionTree.muc6_DecisionTree_goldnps-WordPairBinary"
    #predictions2="predictions.DecisionTree.muc6_DecisionTree_goldnps-LexicoSemanticSundanceBinary"
    #predictions2="predictions.DecisionTree.muc6_DecisionTree_goldnps-SetSundance"
    #predictions2="predictions.DecisionTree.muc6_DecisionTree_goldnps-WordPairBinary"
    predictions2="predictions.DecisionTree.muc6_DecisionTree_goldnps-WordPairBinary-LexicoSemanticSundanceBinary"

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(fileList.readlines())

    total_diff1 = 0
    total_diff2 = 0
    total_overlap = 0
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        print("Working on doc: {0}".format(f))
        response1 = reconcile.getAllResponsePairs(f, "/features." + base + "/" + predictions1)
        system1_pairs = {}
        system2_pairs = {}
        for pair in response1:
            if pair[2] > 0:
                key = "%s:%s" % (pair[0].getID(), pair[1].getID())
                system1_pairs[key] = pair

        response2 = reconcile.getAllResponsePairs(f, "/features." + second+ "/" + predictions2)
        for pair in response2:
            if pair[2] > 0:
                key = "%s:%s" % (pair[0].getID(), pair[1].getID())
                system2_pairs[key] = pair

        set1 = set(system1_pairs.keys())
        set2 = set(system2_pairs.keys())

        diff1 = len(list(set2 - set1)) #the number of pairs labeled in set 1
                                       #that is not in set 2
        diff2 = len(list(set1 - set2)) #the other direction

        total_diff1 += diff1
        total_diff2 += diff2
        total_overlap += len(list(set1 & set2))

    print("Total diff 1: {0}".format(total_diff1))
    print("Total diff 2: {0}".format(total_diff2))
    print("Total diff overlap: {0}".format(total_overlap))
