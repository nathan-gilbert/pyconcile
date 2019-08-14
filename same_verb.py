#!/usr/bin/python
# File Name : same_verb.py
# Purpose :
# Creation Date : 05-11-2011
# Last Modified : Thu 19 May 2011 06:53:40 PM MDT
# Created By : Nathan Gilbert
#
import sys
from collections import defaultdict

import data
import string_match

def getPreNouns(nps, verbs):
    """Returns a dictionary of np,v pairs -> {v1 : [np1,np2...], ... }  """

    pre = defaultdict(list)
    for v in verbs:
        key=v.getText().lower()
        if (key in data.stop_verbs) or (key in data.to_be):
            continue

        for np in nps:
            if np.getEnd()+1 == v.getStart():
                pre[key].append(np)
    return pre

def getPostNouns(nps, verbs):
    """Returns a dictionary of np,v pairs -> {v1 : [np1,np2...], ... }  """
    pass

def fix_order(pairs):
    new_pairs=[]
    for p in pairs:

        text1 = p[0].getText()
        text2 = p[1].getText()

        if string_match.guantlet(text1,text2):
            continue

        if p[0] < p[1]:
            new_pairs.append((p[0],p[1],"same-verb"))
        else:
            new_pairs.append((p[1],p[0],"same-verb"))

    return new_pairs

def getPairs(nps, verbs):
    """ list(Annotations) -> list(tuples(Annotations), "same-verb") """

    #get a string -> verb annot mapping
    text2verb = defaultdict(list)
    for v in verbs:
        key = v.getText().lower()
        text2verb[key].append(v)

    pairs = []
    pre = getPreNouns(nps, verbs)
    for v in pre.keys():
        if len(pre[v]) > 1:
            #print "%s : %s" % (v, ' '.join(map(lambda x : x.getText(),
            #    pre[v])))
            all_pairs = [(pre[v][x],pre[v][y],"same-verb") for y in xrange(len(pre[v])) \
                    for x in xrange(y,len(pre[v])) if x!=y]
            all_pairs = fix_order(all_pairs)
            pairs.extend(all_pairs)
    return pairs

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <first-argument>" % (sys.argv[0])
        sys.exit(1)


