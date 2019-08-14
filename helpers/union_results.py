#!/usr/bin/python
# File Name : union_results.py
# Purpose : Takes two pairwise files and unions the results. ie., if X -> Y in
# A, and Y -> Z in B, then X -> Y -> Z in C
# Creation Date : 07-30-2012
# Last Modified : Mon 11 Feb 2013 01:08:48 PM MST
# Created By : Nathan Gilbert
#
import sys
import os

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <test-list> <combine-list>" % (sys.argv[0])
        sys.exit(1)

    with open(sys.argv[2], 'r') as unionList:
        unionFiles = filter(lambda x : not x.startswith("#"), unionList.readlines())
    with open(sys.argv[1], 'r') as testList:
        testFiles = filter(lambda x : not x.startswith("#"),
                testList.readlines())

    for tf in testFiles:
        tf = tf.strip()
        print "Working on {0}".format(tf)
        final_pairs = {}
        for un in unionFiles:
            un=un.strip()
            response_pairs = reconcile.getResponsePairs2(tf, "/"+un, 0.0)
            print len(response_pairs)
            for pair in response_pairs:
                key = "%s,%d,%d" % (pair[0], pair[1], pair[2])
                if key in final_pairs.keys():
                    final_pairs[key] = pair[3] if (pair[3] > final_pairs[key]) else final_pairs[key]
                else:
                    final_pairs[key] = pair[3]

        outDir="/features.union"
        outFile=outDir+"/predictions.DecisionTree.muc7_DecisionTree_union"
        #outFile=outDir+"/predictions.DecisionTree.muc6_DecisionTree_union"
        outFile=outDir+"/predictions.DecisionTree.promed_DecisionTree_union_0"
        #outFile=outDir+"/predictions.DecisionTree.muc4_DecisionTree_union"
        try:
            os.mkdir(tf + outDir)
            os.mkdir(tf + outFile)
        except OSError:
            pass

        with open(tf + outFile + "/predictions", 'w') as predictFile:
            for un in unionFiles:
                predictFile.write("# %s" % un)
            for key in final_pairs.keys():
                predictFile.write("%s %0.2f\n" % (key, final_pairs[key]))

    print "Finished"
