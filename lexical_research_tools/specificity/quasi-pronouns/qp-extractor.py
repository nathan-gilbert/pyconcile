#!/usr/bin/python
# File Name : common_noun_extractor.py
# Purpose :
# Creation Date : 01-06-2014
# Last Modified : Thu 27 Feb 2014 11:36:20 AM MST
# Created By : Nathan Gilbert
#
import sys
import random

from pyconcile import reconcile
from pyconcile import data
from pyconcile import utils
import qp_utils
from pyconcile.bar import ProgressBar

def collectACEFPs(ace_annots):
    this_files_common_nouns = []
    for gold_np in ace_annots:
        if not gold_np["GOLD_SINGLETON"] and gold_np["is_nominal"]:
            this_files_common_nouns.append(gold_np)
    return this_files_common_nouns

def collectFPs(nps, pos):
    global PROMED, MUC4, MUC6, MUC7
    this_files_common_nouns = []
    for np in nps:
        #determine if common noun
        if qp_utils.isNominal(np,pos):
            this_files_common_nouns.append(np)
    return this_files_common_nouns

def preModification(fp, pos):
    #get the tokens between the determiner and the head.
    #tags = map(lambda x : x["TAG"], pos.getSubset(fp.getStart(), head_end))
    tags = pos.getSubset(fp.getStart(), fp["HEAD_END"])
    #print "{0:20} : {1:20}".format(gold_text, " ".join(tags))
    #skip the first and last tokens [should be det and nn]
    for tag in tags[1:-1]:
        if tag["TAG"] not in ("JJ", "CD"):
            return True
        else:
            #removing 'the Russian leader' <- the adj 'Russian' is
            #too specific
            if (tag["TAG"] == "JJ") and tag.getText()[0].isupper():
                return True
    return False

def isPossessive(fp, pos):
    tags = pos.getSubset(fp.getStart(), fp["HEAD_START"])
    for tag in tags:
        if tag["TAG"] in ("POS", "PRP$"):
            return True
    return False

def isAppositive(fp, tokens):
    for i in range(len(tokens)):
        if tokens.get(i).getEnd() == fp["HEAD_END"]:
            if i+1 <= len(tokens):
                tok = tokens.get(i+1)
                tag = pos.getAnnotBySpan(tok.getStart(),
                        tok.getEnd())["TAG"]
                #check for post modifications
                if tok.getText() in (",", "_"):
                    #print "{0:20} : {1:10} : {2}".format(fp.pprint(),
                    #        tokens.get(i+1).pprint(), tag)
                    return True
                # we are still inside the annotation...skip anything
                # that goes beyond the head in the same annotation
                #if (tok.getEnd() < fp.getEnd()):
                #    return True
    return False

def prePreModification(fp, tokens):
    prev = None
    for i in range(len(tokens)):
        if tokens.get(i).getEnd() < fp.getStart():
            prev = tokens.get(i)
        else:
            break
    return prev

def postPostModification(fp, tokens):
    for i in range(len(tokens)):
        if tokens.get(i).getStart() >= fp.getEnd():
            return tokens.get(i)
    return None

def postModification(fp, tokens):
    #look at the next word after the annotation for post modification
    for i in range(len(tokens)):
        if tokens.get(i).getEnd() == fp["HEAD_END"]:
            if i+1 <= len(tokens):
                tok = tokens.get(i+1)
                tag = pos.getAnnotBySpan(tok.getStart(),
                        tok.getEnd())["TAG"]

                #check for post modifications
                if (tag == "IN") or (tok.getText().lower() in data.relatives) or tok.getText() in (",", "_"):
                    #print "{0:20} : {1:10} : {2}".format(fp.pprint(),
                    #        tokens.get(i+1).pprint(), tag)
                    return True

                # we are still inside the annotation...skip anything
                # that goes beyond the head in the same annotation
                if (tok.getEnd() < fp.getEnd()):
                    return True
    return False

def bareDefinite(text, head):
    #check for pre-modification
    if (text == "the " + head) \
        or (text == "that " + head) \
        or (text == "this " + head) \
        or (text == "those " + head) \
        or (text == "these " + head):
        return True
    return False

ACE=False
MUC4=False
MUC6=False
MUC7=False
PROMED=False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist> <qps>" % (sys.argv[0])
        sys.exit(1)

    COMMENT = "These are all potential faux pronouns: any non-singleton, common noun."
    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    qps = []
    with open(sys.argv[2], 'r') as qpList:
        for line in qpList:
            if line.startswith("#"): continue
            line = line.strip()
            qps.append(line)

    if sys.argv[1].find("ace") > -1:
        ACE = True
        qp_utils.set_dataset("ACE")
    else:
        ACE = False

    if sys.argv[1].find("muc4") > -1:
        MUC4 = True
        qp_utils.set_dataset("MUC4")
    else:
        MUC4 = False

    if sys.argv[1].find("muc6") > -1:
        MUC6 = True
        qp_utils.set_dataset("MUC6")
    else:
        MUC6 = False

    if sys.argv[1].find("muc7") > -1:
        MUC7 = True
        qp_utils.set_dataset("MUC7")
    else:
        MUC7 = False

    if sys.argv[1].find("promed") > -1:
        PROMED = True
        qp_utils.set_dataset("PROMED")
    else:
        PROMED = False

    prog = ProgressBar(len(files))
    j=0
    total_qps_created = 0
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        prog.update_time(j)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        j+=1

        this_files_faux_pronouns = []
        tokens = reconcile.getTokens(f)
        pos = reconcile.getPOS(f)
        #read in all possible quasi pronouns
        if ACE:
            ace_annots = reconcile.parseGoldAnnots(f)
            faux_pronouns = collectACEFPs(ace_annots)
        else:
            nps = reconcile.getNPs(f)
            faux_pronouns = collectFPs(nps, pos)

        for fp in faux_pronouns:
            text = utils.textClean(fp.getText()).lower().strip()
            if ACE:
                head = fp["HEAD"].lower().strip()
            else:
                np_tags = pos.getSubset(fp.getStart(), fp.getEnd())
                head = qp_utils.getHead2(text, np_tags).lower().strip()

            #NOTE select what types of modification to allow on QPs here.
            #select only qps and bare definites
            #if (head in qps) and bareDefinite(text, head):
            #    this_files_faux_pronouns.append(fp)

            #all QPs regardless of modification
            if head in qps:
                this_files_faux_pronouns.append(fp)

            #random nominals
            #r_num = random.random()
            #if r_num >= 0.50:
            #    this_files_faux_pronouns.append(fp)

            #preToken = prePreModification(fp, tokens)
            #if preToken is None:
            #    preToken = "none"
            #else:
            #    preToken = preToken.getText()
            #postToken = postPostModification(fp, tokens)
            #if postToken is None:
            #    postToken = "none"
            #else:
            #    postToken = postToken.getText()

        #print out the fp and this is the new 
        i = 0
        with open(f+"/annotations/faux_pronouns", 'w') as outFile:
            outFile.write("#"+f+"\n")
            outFile.write("#"+COMMENT+"\n")
            for annot in this_files_faux_pronouns:
                total_qps_created += 1
                outFile.write("{0}\t{1},{2}\t{3}\t\n".format(i,annot.getStart(),
                    annot.getEnd(), utils.textClean(annot.getText().lower())))
                i+=1
    sys.stderr.write("\r \r\n")
    print "{0} QPs written".format(total_qps_created)
