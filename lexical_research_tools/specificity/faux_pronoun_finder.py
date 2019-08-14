#!/usr/bin/python
# File Name : faux_pronoun_finder.py
# Purpose :
# Creation Date : 11-25-2013
# Last Modified : Mon 25 Nov 2013 04:45:51 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile.annotation_set import AnnotationSet

#NOTE: FAUX PRONOUN Definition:
#      1. semantically general 
#      2. definite NP?
#      3. no substantive pre or post modification
#      4. % of bare def uses vs. bare indef uses
#      5. diversity and propensity scores (for labeled data?) could it be
#      modeled by the number of senses in WN? 
#      6. 'concreteness' of word

ACE = False

#get all common nouns [this is easy for ACE]
def getACECommonNouns(f):
    nps = reconcile.getNPs(f)
    gold_nps = reconcile.parseGoldAnnots(f)
    common_nps = AnnotationSet("common_nouns")
    for np in nps:
        gold_np = gold_nps.getAnnotBySpan(np.getStart(), np.getEnd())
        if not gold_np["GOLD_SINGLETON"] and gold_np["is_nominal"]:
            common_nps.add(np)
    return common_nps

def getCommonNouns(f):
    if ACE:
        return getACECommonNouns(f)
    return []

#TODO: label the semantically general ones
def labelSpecificity(w):
    pass

#TODO: find pre or post modification
def modification(w):
    pass

#TODO: diversity / propensity from a labeled corpus [I can actually do this
#                                                    with ACE.]
#TODO: see if diversity / propensity can be modeled by the number of senses in
#      WN?
def diversity(w):
    pass

#TODO: pull in concreteness and use it
def concreteness(w):
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list> [-ACE]" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    if "-ACE" in sys.argv:
        ACE = True

    for f in files:
        f=f.strip()
        print("Working on file: {0}".format(f))

        nominals = getCommonNouns(f)
        for cn in nominals:
            print(cn.pprint())

