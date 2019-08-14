#!/usr/bin/python
# File Name : errors.py
# Purpose : 
# Creation Date : 12-07-2010
# Last Modified : Thu 08 Dec 2011 01:50:49 PM MST
# Created By : Nathan Gilbert
# TODO/BUGS: 
# 1. 
import sys
from optparse import OptionParser
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import score
from pyconcile import duncan
from pyconcile.annotation_set import AnnotationSet

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file", help="The file to check.",
            action="store", dest="directory", type="string", default=None)
    parser.add_option("-l", "--filelist", help="File list",
            action="store", dest="filelist", type="string", default=None)
    parser.add_option("-p", "--predictions", help="Which predictions to use",
            action="store", dest="predictions", type="string", default="")
    parser.add_option("-d", "--Duncan", help="What duncan annots to use",
            action="store", dest="duncan", type="string", default="")
    parser.add_option("-v", help="Verbose. Be it.", action="store_true", dest="verbose", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    if options.directory is not None:
        gold_chains = reconcile.getGoldChains(options.directory)
        duncan_pairs = duncan.getDuncanPairs(options.directory)
        accuracy = score.accuracy(gold_chains, duncan_pairs)
        print("A: %d/%d = %0.2f" % (accuracy[0], accuracy[1], accuracy[2]))
    elif options.filelist is not None:
        filelist = open(options.filelist, 'r')
        total = [0, 0]
        h_stats_correct = {}
        h_stats_total = {}
        for f in filelist:
            f=f.strip()
            if f.startswith("#"):
                continue
            gold_chains = reconcile.getGoldChains(f)
            duncan_pairs = duncan.getDuncanPairs(f)
            accuracy = score.accuracy(gold_chains, duncan_pairs)
            print("Doc %s A: %d/%d = %0.2f" % (f, accuracy[0], accuracy[1], accuracy[2]))
            total[0] += accuracy[0]
            total[1] += accuracy[1]

            #get the heuristic score  
            for pair in duncan_pairs:
                antecedent = pair[0]
                anaphor = pair[1]

                h = anaphor.getATTR("H")
                h_stats_total[h] = h_stats_total.get(h, 0) + 1
                if score.correctpair(gold_chains, antecedent, anaphor):
                    h_stats_correct[h] = h_stats_correct.get(h, 0) + 1

        print("Total A: %d/%d = %0.2f" % (total[0], total[1],
                float(total[0])/total[1]))

        print("Heuristic break down")
        keys = set(list(h_stats_correct.keys()) + list(h_stats_total.keys()))
        for k in keys:
            correct = h_stats_correct.get(k, 0)
            incorrect = h_stats_total.get(k, 0)
            print("%s: %d/%d %0.2f" % (k, correct, incorrect,
                    float(correct)/incorrect))
