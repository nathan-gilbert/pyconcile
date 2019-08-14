#!/usr/bin/python
# File Name : discourse_new.py
# Purpose : P(1st item in chain | x is in chain), heads, modifiers
# Creation Date : 10-02-2012
# Last Modified : Mon 08 Oct 2012 01:34:08 PM MDT
# Created By : Nathan Gilbert
#
import sys
import operator

from pyconcile import reconcile
from pyconcile import utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list>" % (sys.argv[0]))
        sys.exit(1)

    files=[]
    with open(sys.argv[1], 'r') as file_list:
        files.extend(file_list.readlines())

    dn = {}
    total_counts = {}
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        print("Working on document: {0}".format(f))

        tokens = reconcile.getTokens(f)
        pos = reconcile.getPOS(f)

        #grab the gold chains
        gold_chains=reconcile.getGoldChains(f)

        #loop over them and keep track of the terms that are discourse_new
        for gc in list(gold_chains.keys()):
            first=True
            for mention in gold_chains[gc]:
                #add in tokens and tags
                mention_pos = [x.getATTR("TAG") for x in pos.getOverlapping(mention)]
                mention_tok = [x.getText() for x in tokens.getOverlapping(mention)]
                mention.setProp("TAGS", mention_pos)
                mention.setProp("TOKENS", mention_tok)

                #get the head
                mention_head = utils.getHead(mention)

                if first:
                    #keep track of the first mention, it's the discourse_new
                    first=False

                    #keep track of how many times a particular head appears in all chains
                    dn[mention_head] = dn.get(mention_head, 0) + 1

                total_counts[mention_head] = total_counts.get(mention_head, 0) + 1
    dn_prob = {}
    for key in list(dn.keys()):
        dn_prob[key] = float(dn[key]) / total_counts[key]

    sorted_probs = sorted(iter(dn_prob.items()), key=operator.itemgetter(1),
            reverse=True)

    num = 0 
    for i in range(len(sorted_probs)):
        if total_counts[sorted_probs[i][0]] < 2:
            continue

        print("{0} : {1} : {2}".format(sorted_probs[i][0], sorted_probs[i][1],
                total_counts[sorted_probs[i][0]]))
        num += 1

        if num > 100:
            break
