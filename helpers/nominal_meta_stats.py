#!/usr/bin/python
# File Name : nominal_meta_stats.py
# Purpose : A script to collect stats about the stats generated from
# "master_nominal_stats.py"
# Creation Date : 11-10-2011
# Last Modified : Thu 17 Nov 2011 02:11:50 PM MST
# Created By : Nathan Gilbert
#
# Notes on what to collect:
# 1. How many NPs from test set are covered by statistics?
#  a. Remember that different features will have coverage of different NPs
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <test-files> <lexical_stats>" % (sys.argv[0])
        sys.exit(1)

    #read in lexical stats
    commons = []
    stats_file = open(sys.argv[2], 'r')
    for line in stats_file:
        if line.startswith("TEXT:"):
            text = line.replace("TEXT:","").strip()
            commons.append(text)
    stats_file.close()

    test_docs = open(sys.argv[1], 'r')

    found_gold = 0
    found_response = 0
    total_gold_nps = 0
    total_response_nps = 0
    for doc in test_docs:
        doc=doc.strip()
        gold_nps = reconcile.parseGoldAnnots(doc)
        response_nps = reconcile.getNPs_annots(doc)

        for a in gold_nps:
            total_gold_nps += 1
            #print a.getATTR("TEXT_CLEAN").lower()
            if a.getATTR("TEXT_CLEAN").lower() in commons:
                found_gold += 1

        for a in response_nps:
            total_response_nps += 1
            if a.getATTR("TEXT_CLEAN").lower() in commons:
                found_response+=1
    test_docs.close()

    print "Found: %d/%d (%0.2f) from stats" % (found_gold, len(commons),
            float(found_gold)/len(commons))
    print "Found %d/%d (%0.2f) from gold" % (found_gold, total_gold_nps,
            float(found_gold)/total_gold_nps)
    print "Found %d/%d (%0.2f) from response" % (found_response, total_response_nps,
            float(found_response)/total_response_nps)


