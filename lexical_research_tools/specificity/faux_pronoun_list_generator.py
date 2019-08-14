#!/usr/bin/python
# File Name : common_noun_list_generator.py
# Purpose :
# Creation Date : 11-05-2013
# Last Modified : Fri 08 Nov 2013 04:09:16 PM MST
# Created By : Nathan Gilbert
#
import sys
import re

import specificity_utils
from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"), fileList.readlines()))

    heads = []
    for f in files:
        f=f.strip()
        print "Working on {0}".format(f)
        common_nouns = reconcile.getFauxPronouns(f)

        for cn in common_nouns:
            text = utils.textClean(cn.getText().replace("\n", " ")).lower()
            head = specificity_utils.getHead(text).rstrip('\'\"-,.:;!?')

            if head in data.ALL_PRONOUNS:
                continue

            if head not in heads:
                heads.append(head)

    with open("{0}_faux_pronouns".format(sys.argv[1]), 'w') as outFile:
        for head in heads:
            if len(re.findall(r'\w+', head)) > 1:
                continue
            outFile.write("{0}\n".format(head))

