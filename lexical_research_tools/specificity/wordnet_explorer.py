#!/usr/bin/python
# File Name : wordnet_explorer.py
# Purpose :
# Creation Date : 08-27-2013
# Last Modified : Wed 28 Aug 2013 03:08:42 PM MDT
# Created By : Nathan Gilbert
#
import sys
import en

from pyconcile import reconcile
from pyconcile import utils
import specificity_utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <dir>" % (sys.argv[0])
        sys.exit(1)

    #read in the nps
    nps = reconcile.getNPs(sys.argv[1])

    for np in nps:
        if specificity_utils.isProper(np) or specificity_utils.isPronoun(np):
            continue
        head = specificity_utils.getHead(utils.textClean(np.getText()))
        print "{0} => {1}".format(np.pprint(),head)
        print en.noun.senses(head)
        print en.noun.hypernyms(head, sense=0)
        print "="*30

    #read in named entities and/or read the 
    #fire up wordnet


