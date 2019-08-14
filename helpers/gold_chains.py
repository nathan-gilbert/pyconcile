#!/usr/bin/python
# File Name : gold_chains.py
# Purpose :
# Creation Date : 11-22-2011
# Last Modified : Tue 26 Nov 2013 11:32:03 AM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s dir" % (sys.argv[0])
        sys.exit(1)

    gold_chains = reconcile.getGoldChains(sys.argv[1])

    if "-m" not in sys.argv:
        for k in gold_chains.keys():
            #if len(gold_chains[k]) < 2:
            #    continue
            print "{ ",
            print "%s" % (" \n\t<- ".join(map(lambda x :
            x.ppprint().replace("\n", " "), gold_chains[k]))),
            print "\n}"
    else:
        for k in gold_chains.keys():
            print "{ ",
            print "%s" % (" \n\t<- ".join(map(lambda x :
            x.pppprint().replace("\n", " "), gold_chains[k]))),
            print "\n}"
