#!/usr/bin/python
# File Name : common_noun_extractor.py
# Purpose :
# Creation Date : 01-06-2014
# Last Modified : Tue 14 Jan 2014 12:47:57 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import data
from pyconcile import utils
import qp_utils

ACE=False

def collectACECommonNouns(ace_annots):
    this_files_common_nouns = []
    for gold_np in ace_annots:
        if not gold_np["GOLD_SINGLETON"] and gold_np["is_nominal"]:
            this_files_common_nouns.append(gold_np)
    return this_files_common_nouns

def collectCommonNouns(nps, pos):
    this_files_common_nouns = []
    for np in nps:
        #determine if common noun
        if qp_utils.isNominal(np,pos):
            this_files_common_nouns.append(np)
    return this_files_common_nouns

def collectProperNouns(nps, pos):
    global PROMED, MUC4, MUC6, MUC7
    this_files_proper_nouns = []
    for np in nps:
        #determine if common noun
        if qp_utils.isProper(np,pos):
            this_files_proper_nouns.append(np)
    return this_files_proper_nouns

def collectPronouns(nps):
    this_files_pronouns = []
    for np in nps:
        text = np.getText().lower()
        if text in data.ALL_PRONOUNS:
            this_files_pronouns.append(np)
    return this_files_pronouns

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    if sys.argv[1].find("ace") > -1:
        ACE = True
        qp_utils.set_dataset("ACE")

    if sys.argv[1].find("muc4") > -1:
        qp_utils.set_dataset("MUC4")

    if sys.argv[1].find("muc6") > -1:
        qp_utils.set_dataset("MUC6")

    if sys.argv[1].find("muc7") > -1:
        qp_utils.set_dataset("MUC7")

    if sys.argv[1].find("promed") > -1:
        qp_utils.set_dataset("PROMED")

    wordlist = []
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()

        tokens = reconcile.getTokens(f)
        pos = reconcile.getPOS(f)

        common_nouns = []
        proper_nouns = []
        pronouns     = []

        #read in the faux pronouns
        if ACE:
            ace_annots = reconcile.parseGoldAnnots(f)
        else:
            nps = reconcile.getNPs(f)
            common_nouns = collectCommonNouns(nps, pos)
            proper_nouns = collectProperNouns(nps, pos)
            pronouns = collectPronouns(nps)

        for np in proper_nouns:
            text = utils.textClean(np.getText()).lower().strip()
            tags = pos.getSubset(np.getStart(), np.getEnd())
            head = qp_utils.getHead2(text, tags)
            print "{0:7} {1:60} => {2}".format("PROPER:", text, head)

        for np in common_nouns:
            text = utils.textClean(np.getText()).lower().strip()
            tags = pos.getSubset(np.getStart(), np.getEnd())
            head = qp_utils.getHead2(text, tags)
            print "{0:7} {1:60} => {2}".format("COMMON:", text, head)

        for np in pronouns:
            text = utils.textClean(np.getText()).lower().strip()
            tags = pos.getSubset(np.getStart(), np.getEnd())
            head = qp_utils.getHead2(text, tags)
            print "{0:8} {1:60} => {2}".format("PRONOUN:", text, head)

