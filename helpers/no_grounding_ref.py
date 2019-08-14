#!/usr/bin/python
# File Name : no_grounding_ref.py
# Purpose :
# Creation Date : 11-10-2011
# Last Modified : Mon 21 Nov 2011 11:17:48 AM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list>" % (sys.argv[0]))
        sys.exit(1)

    fileList = open(sys.argv[1], 'r')
    files = [x for x in fileList.readlines() if not x.startswith("#")]
    no_grounding_refs = []
    all_nominals = []

    for f in files:
        f = f.strip()
        print("Working on document: %s" % f)
        gold_chains = reconcile.getGoldChains(f, True)
        #read in all the gold chains
        for gc in list(gold_chains.keys()):
            #determine if any of the nominals are in fact in a chain with no
            #grounding reference.
            for mention in gold_chains[gc]:
                if not mention.getATTR("is_nominal"):
                    break
                else:
                    all_nominals.append(mention)
            else:
                no_grounding_refs.append(gold_chains[gc])

        #keep track of 1. what doc they are from
        #              2. how many entities in chain
        #              3. semantic class
        #              4. distances between mentions
        #              5. how many other nominals are in chains in this doc?
        #              6. 

    for c in no_grounding_refs:
        print(set([x.pprint() for x in c]))


    l=[]
    for n in all_nominals:
        for c in no_grounding_refs:
            if n in c:
                break
        else:
            l.append(n.pprint())

    print(set(l))
