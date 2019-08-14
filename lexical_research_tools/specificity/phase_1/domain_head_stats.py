#!/usr/bin/python
# File Name : domain_head_stats.py
# Purpose : Locate and identify key stats for evaluating VP hypothesis.
# Creation Date : 05-24-2013
# Last Modified : Wed 29 May 2013 10:49:49 AM MDT
# Created By : Nathan Gilbert
#
import sys
import os
import operator

from pyconcile import reconcile
from pyconcile import utils
import specificity_utils
from pyconcile.bar import ProgressBar

class Noun:
    def __init__(self, h):
        self.head = h
        self.texts = []
        self.count = 0    #total counts
        self.docs = {}    #doc2counts
        self.definite = {
                            "indefinite" : 0,
                            "definite"   : 0,
                            "bare"       : 0,
                        }
        self.noun_mods = []
        self.adj_mods  = []
        self.of_attachments = []  #fill with examples of 'X'
        self.recent_proper_names = []
        self.recent_semantic_classes = []
        self.ba   = 0
        self.subj = 0
        self.dobj = 0

    def addText(self, t):
        self.texts.append(t)

    def addDoc(self, d):
        self.docs[d] = self.docs.get(d, 0) + 1

    #TODO
    def addMods(self, mods):
        pass

    def addDefinite(self, orig):
        orig_text = utils.textClean(orig.getText())
        if orig_text.startswith("the "):
            self.definite["definite"] = self.definite.get("definite", 0) + 1
        elif orig_text.startswith("a ") or orig_text.startswith("an "):
            self.definite["indefinite"] = self.definite.get("indefinite", 0) + 1
        else:
            if orig_text == self.head:
                self.definite["bare"] = self.definite.get("bare", 0) + 1

    def __str__(self):
        try:
            definite = float(self.definite.get("definite", 0)) / self.count
        except:
            definite = 0.0

        try:
            indefinite = float(self.definite.get("indefinite", 0)) / self.count
        except:
            indefinite = 0.0

        try:
            bare = float(self.definite.get("bare", 0)) / self.count
        except:
            bare = 0.0

        try:
            mentions_per_doc = float(self.count) / len(self.docs.keys())
        except:
            mentions_per_doc = 0.0

        try:
            median_mentions_per_doc = specificity_utils.median(self.docs.values())
        except:
            median_mentions_per_doc = 0.0

        try:
            ba = float(self.ba) / self.count
        except:
            ba = 0.0

        try:
            subj = float(self.subj) / self.count
        except:
            subj = 0.0

        try:
            dobj = float(self.dobj) / self.count
        except:
            dobj = 0.0 

        s = "{0:15} {1:5} {2:4} {3:0.2f} {4:0.2f} {5:0.2f} {6:0.2f} {7:0.2f} {8:0.2f} {9:0.2f} {10:0.2f}".format(
                self.head,
                self.count,
                len(self.docs.keys()),
                definite,
                indefinite,
                bare,
                mentions_per_doc,
                median_mentions_per_doc,
                ba,
                subj,
                dobj
                )
        return s

def getSentence(np, sent):
    for s in sent:
        if s.contains(np):
            return s["NUM"]
    return -1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist> <headlist>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        for line in fileList:
            if line.startswith("#"): continue
            line = line.strip()
            files.append(line)

    heads = []
    with open(sys.argv[2], 'r') as headFile:
        for line in headFile:
            if line.startswith("head") : continue #skip the first line
            line = line.strip()
            if line == "": continue #skip blank lines
            tokens = line.split()
            heads.append(tokens[0])

    #create the dict of heads
    head2nouns = {}
    for head in heads:
        head2nouns[head] = Noun(head)

    #cycle over all the files
    #sys.stdout.flush()
    #sys.stdout.write("\r")
    #prog = ProgressBar(len(files))
    i = 0
    for f in files:
        #prog.update_time(i)
        #sys.stdout.write("\r%s" % (str(prog)))
        #sys.stdout.flush()
        i+=1
        #read in the nps
        nps = reconcile.getNPs(f)
        sentences = reconcile.getSentences(f)

        #see which nps correspond to these heads
        for np in nps:
            np_text = utils.textClean(np.getText())
            np_head = specificity_utils.getHead(np_text)

            if np_head in heads:
                #print "{0:35} => {1}".format(np_text, np_head)
                head2nouns[np_head].addDoc(f)
                head2nouns[np_head].addText(np_text)
                head2nouns[np_head].count += 1
                head2nouns[np_head].addDefinite(np)

                if np["GRAMMAR"] == "SUBJECT":
                    head2nouns[np_head].subj +=1
                elif np["GRAMMAR"] == "OBJECT":
                    head2nouns[np_head].dobj +=1

                np_sentence = getSentence(np, sentences)
                if np_sentence == 0:
                    head2nouns[np_head].ba += 1

    #sys.stdout.write("\r \r\n")
    #os.system("clear")
    sorted_nouns = sorted(head2nouns.values(), key=operator.attrgetter('count'), reverse=True)
    print "{0:15} {1:5} {2:4} {3:>4} {4:>4} {5:>4} {6:>4} {7:>4} {8:>4} {9:>4} {10:>4}".format("head", "count", "docs", "D", "I", "B", "MD", "MMD", "fBA", "S", "O")
    print

    for noun in sorted_nouns:
        if len(noun.docs.keys()) < 3:
            continue
        print noun

