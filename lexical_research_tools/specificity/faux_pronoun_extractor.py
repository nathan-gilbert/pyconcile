#!/usr/bin/python
# File Name : common_noun_extractor.py
# Purpose :
# Creation Date : 10-28-2013
# Last Modified : Tue 03 Dec 2013 10:46:28 AM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data
import specificity_utils

#uses gold NPs and gold heads
def collectACEFPs(ace_annots, this_files_common_nouns):
    for gold_np in ace_annots:
        if gold_np is not None:
            #if not gold_np["GOLD_SINGLETON"] and np["GRAMMAR"] == "SUBJECT":
            if not gold_np["GOLD_SINGLETON"] and gold_np["is_nominal"]:
                gold_text = utils.textClean(gold_np.getText()).lower().strip()
                gold_head = gold_np["HEAD"].lower().strip()
                #definites + demonstratives
                if gold_text in ("the "+gold_head, "that "+gold_head, "this "+gold_head, "these "+gold_head, "those "+gold_head):
                    this_files_common_nouns.append(gold_np)
        else:
            print "couldn't find {0} in the gold".format(np)

def collectFPs(gold_nps, this_files_common_nouns):
    for np in gold_nps:
        if specificity_utils.isNominal(np):
            this_files_common_nouns.append(np)

            #txt = utils.textClean(np.getText()).lower()
            #if txt not in common_nps:
            #    common_nps.append(txt)
        #else:
        #    txt = utils.textClean(np.getText()).lower()
        #    if txt not in not_common_nps:
        #        not_common_nps.append(txt)

def checkForModification(fp, tokens, pos):
    #end = fp.getEnd()
    end = fp["HEAD_END"]

    #look at the next word after the annotation
    for i in range(len(tokens)):
        if tokens.get(i).getEnd() == end:
            #go one token beyond the head
            if i+1 <= len(tokens):
                tok = tokens.get(i+1)
                #if there is *any* post modification inside of the annotation, skip
                #it.
                if tok.getEnd() <= fp.getEnd():
                    print "Removing {0:20}".format(fp.pprint())
                    return True

                tag = pos.getAnnotBySpan(tok.getStart(),tok.getEnd())["TAG"]
                if (tag == "IN") or (tok.getText().lower() in data.relatives):
                    print "Removing {0:20} : {1:10} : {2}".format(fp.pprint(),
                            tokens.get(i+1).pprint(), tag)
                    return True
                else:
                    return False
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-list> [-ace]" % (sys.argv[0])
        sys.exit(1)

    #if working with ACE data, read in the ACE annots and only 
    #create a VP for non-singleton mentions
    ACE = False
    if "-ace" in sys.argv:
        ACE = True

    common_nps = []
    not_common_nps = []
    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    #if ACE:
        #with open(sys.argv[2], 'r') as aceFile:
        #    used = []
        #    for line in aceFile:
        #        line = line.strip()
        #        if line.startswith("#"): continue
        #        #if line not in ACE_HEADS:
        #        if line not in used:
                    #set up for bare definites
        #            ACE_HEADS.append("the " + line)
        #            ACE_HEADS.append("that " + line)
        #            ACE_HEADS.append("this " + line)
        #            used.append(line)
                    #set up for all commons
                    #ACE_HEADS.append(line)

    for f in files:
        f=f.strip()
        print "Working on file: {0}".format(f)
        this_files_common_nouns = []
        if ACE:
            tokens = reconcile.getTokens(f)
            pos = reconcile.getPOS(f)
            ace_annots = reconcile.parseGoldAnnots(f)
            this_files_common_nouns_orig = []
            collectACEFPs(ace_annots, this_files_common_nouns_orig)

            #remove post modded commons
            for fp in this_files_common_nouns_orig:
                if not checkForModification(fp, tokens, pos):
                    this_files_common_nouns.append(fp)
        else:
            gold_nps = reconcile.getNPs(f)
            collectFPs(gold_nps, this_files_common_nouns)

        #output common nouns to file
        i = 0
        with open(f+"/annotations/faux_pronouns", 'w') as outFile:
            for annot in this_files_common_nouns:
                outFile.write("{0}\t{1},{2}\t{3}\t\n".format(i,annot.getStart(),
                    annot.getEnd(), utils.textClean(annot.getText().lower())))
                i+=1

