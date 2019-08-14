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
        print("Usage: %s dir" % (sys.argv[0]))
        sys.exit(1)

    gold_chains = reconcile.getGoldChains(sys.argv[1])

    if "-m" not in sys.argv:
        for k in list(gold_chains.keys()):
            #if len(gold_chains[k]) < 2:
            #    continue
            print("{ ", end=' ')
            print("%s" % (" \n\t<- ".join([x.ppprint().replace("\n", " ") for x in gold_chains[k]])), end=' ')
            print("\n}")
    else:
        for k in list(gold_chains.keys()):
            print("{ ", end=' ')
            print("%s" % (" \n\t<- ".join([x.pppprint().replace("\n", " ") for x in gold_chains[k]])), end=' ')
            print("\n}")
