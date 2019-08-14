#!/usr/bin/python
# File Name : gold_annots_list.py
# Purpose : Print out all the unique gold annotations
# Creation Date : 12-14-2011
# Last Modified : Wed 01 Aug 2012 01:18:47 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string

from pyconcile import reconcile
from pyconcile import utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-list>" % (sys.argv[0])
        sys.exit(1)

    fList=open(sys.argv[1], 'r')
    #gold = {}
    gold = []

    for f in fList:
        if f.startswith("#"):
            continue
        f=f.strip()
        gold_annots = reconcile.parseGoldAnnots(f)
        for g in gold_annots:
            #if g.getText() not in gold.keys():
            if g.getText() not in gold:
                text= ' '.join(map(string.strip, g.getText().replace("\n",
                    "").split()))

                #need to get tags and tokens for this NP
                #pos = []
                #head = utils.getHead(g)
                #gold[text] = (head, pos)
                gold.append(text)
    for t in gold:
        print t
