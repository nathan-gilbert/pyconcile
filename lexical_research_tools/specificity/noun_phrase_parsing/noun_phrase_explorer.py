#!/usr/bin/python
# File Name : noun_phrase_explorer.py
# Purpose :
# Creation Date : 08-28-2013
# Last Modified : Thu 07 Nov 2013 09:39:28 AM MST
# Created By : Nathan Gilbert
#
import sys
import re

from pyconcile import reconcile
from pyconcile import utils

class NP:
    def __init__(self, t):
        self.start = -1
        self.end = -1
        self.text = t
        self.annotations = {
                "HEAD" : (-1, -1)
            }
        self.adj_mod = False
        self.prp_mod = False
        self.nom_mod = False
        self.other_mod = False
        self.possessive_mod = False
        self.clause_post_mod = False
        self.prep_post_mod = False

    #head
    def addHead(self, span):
        self.annotations["HEAD"] = span

    #proper name
    def addPN(self, span):
        self.annotations["PN"] = span

    #semantic class in NP
    def addSC(self, span):
        self.annotations["SC"] = span

    #possessive
    def addPossessive(self, span):
        self.annotations["Poss"] = span

    def addAdjective(self, span):
        self.annotations["Adj"] = span

    def hasAdjMod(self):
        self.adj_mod = True

    def hasPrpMod(self):
        self.prp_mod = True

    def hasNomMod(self):
        self.nom_mod = True

    def hasOtherMod(self):
        self.other_mod = True

    def hasPossessiveMod(self):
        self.possessive_mod = True

    def hasClausePostMod(self):
        self.clause_post_mod = True

    def hasPrepPostMod(self):
        self.prep_post_mod = True

    def __str__(self):
        return "{0} : {1}".format(self.text, self.annotations)

def getHeadSpan(annot, head):
    #NOTE: texts with parenths have problems
    if annot.getText().find("(") > -1 or annot.getText().find(")") > -1:
        return None
    match = re.compile(r'\b({0})\b'.format(head), flags=re.IGNORECASE).search(utils.textClean(annot.getText()))
    if match:
        return (match.start(1), match.end(1)-1)
    return None

def getHead(text):
    """duplicates the head generation in java"""
    text = text.strip()

    #check if conjunction
    if utils.isConj(text):
        return utils.conjHead(text)

    tokens = text.split()
    new_text = ""
    first = True
    for word in tokens:
        if (utils.break_word(word) and not first):
            break

        if (word.endswith(",")):
            new_text += word[:-1]
            break

        new_text += word + " "
        first = False

    new_text = new_text.strip()
    if new_text == "":
        sys.stderr.write("Empty text: \"{0}\" : \"{1}\"".format(text, new_text))

    head = new_text.split()[-1]
    if head.endswith("'s"):
        head = head.replace("'s","")
    return head

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    #let's look at some noun phrases for each domain.
    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    for f in files:
        f=f.strip()
        print("Working on file: {0}".format(f))
        allNPs = {}
        nps = reconcile.getNPs(f)
        pos = reconcile.getPOS(f)
        stanford_nes = reconcile.getNEs(f)
        sundance_nes = reconcile.getSundanceNEs(f)

        for np in nps:
            key = "{0},{1}".format(np.getStart(), np.getEnd())
            text = utils.textClean(np.getText().replace("\n", " ")).lower()
            tokens = text.split()
            if len(tokens) == 1:
                continue

            if key not in list(allNPs.keys()):
                allNPs[key] = NP(np.getText().replace("\n", " "))
                allNPs[key].start = np.getStart()
                allNPs[key].end = np.getEnd()

            head = getHead(text)
            head_span = getHeadSpan(np, head)

            if head_span is not None:
                allNPs[key].addHead(head_span)
                #check to see if the head is contain in a proper name
                #if np["contains_pn"] is not None:
                #    pn_start = int(np["pn_start"])
                #    pn_end   = int(np["pn_end"]) - 1

                #    if head_span[0] >= pn_start and head_span[1] <= pn_end:
                #        head_span = (pn_start,pn_end)
                #    else:
                        #then we have a proper name somewhere in the NP.
                        #really need to figure out where it is, a premodifier
                        #or post modifier
                #        pn_span = (pn_start, pn_end)
                #        allNPs[key].addPN(pn_span)

                #for ne in stanford_nes:
                #    if ne.getStart() >= np.getStart() and ne.getEnd() <= np.getEnd():
                #        ne_start = ne.getStart() - np.getStart()
                #        ne_end   = ne.getEnd() - np.getStart() - 1
                #        if (ne_end < head_span[0]) or (ne_start > head_span[1]):
                #            allNPs[key].addSC((ne_start, ne_end))

                #for ne in sundance_nes:
                #    if ne.getStart() >= np.getStart() and ne.getEnd() <= np.getEnd():
                #        ne_start = ne.getStart() - np.getStart()
                #        ne_end   = ne.getEnd() - np.getStart() - 1
                #        if (ne_end < head_span[0]) or (ne_start > head_span[1]):
                #            allNPs[key].addSC((ne_start, ne_end))

                #cycle over all the POS tags for this NP
                pos_subset = pos.getSubset(np.getStart(), np.getEnd())
                for tag in pos_subset:
                    #we have found the head
                    if tag.getStart() >= (head_span[0] + np.getStart()):
                        break

                    #look for pre-mods that are adjs or nouns 
                    if tag["TAG"].startswith("DT"):
                        continue
                    elif tag["TAG"].startswith("JJ"):
                        allNPs[key].hasAdjMod()
                    elif tag["TAG"] == "PRP$" or tag["TAG"] == "POS":
                        allNPs[key].hasPossessiveMod()
                    elif tag["TAG"].startswith("N"):
                        if tag["TAG"].startswith("NNP"):
                            allNPs[key].hasPrpMod()
                        else:
                            allNPs[key].hasNomMod()
                    else:
                        allNPs[key].hasOtherMod()

                #look for post mods [of, with, who, that, at] after head
                if text.find(" that ") > -1:
                    clause_start = text.find(" that ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasClausePostMod()
                if text.find(head + " with ") > -1:
                    clause_start = text.find(head + " with ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasClausePostMod()
                if text.find(head + " which ") > -1:
                    clause_start = text.find(head + " which ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasClausePostMod()
                if text.find(head + " who ") > -1:
                    clause_start = text.find(head + " who ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasClausePostMod()

                if text.find(head + " by ") > -1:
                    clause_start = text.find(head + " by ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasPrepPostMod()
                if text.find(head + " of ") > -1:
                    clause_start = text.find(head + " of ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasPrepPostMod()
                if text.find(head + " of ") > -1:
                    clause_start = text.find(head + " at ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasPrepPostMod()
                if text.find(head + " of ") > -1:
                    clause_start = text.find(head + " in ")
                    if clause_start > head_span[1]:
                        allNPs[key].hasPrepPostMod()

        #output the mod results
        with open(f + "/annotations/mods", 'w') as outFile:
            i=0
            for key in list(allNPs.keys()):
                props = \
                "ADJ=\"{0}\"\tPRP=\"{1}\"\tNOM=\"{2}\"\tOTH=\"{3}\"\tPOSS=\"{4}\"\tCLA=\"{5}\"\tPREP=\"{6}\"".format(allNPs[key].adj_mod,
                        allNPs[key].prp_mod,
                        allNPs[key].nom_mod,
                        allNPs[key].other_mod,
                        allNPs[key].possessive_mod,
                        allNPs[key].clause_post_mod,
                        allNPs[key].prep_post_mod)

                outFile.write("{0}\t{1},{2}\t{3}\tText=\"{4}\"\t\n".format(i,allNPs[key].start,
                    allNPs[key].end, props, allNPs[key].text))
                i+=1

    #old way of printing
    #for key in allNPs.keys():
        #head_span = allNPs[key].annotations["HEAD"]
        #if head_span is not None:
            #pn_span = allNPs[key].annotations.get("PN", (-1,-1))
            #sc_span = allNPs[key].annotations.get("SC", (-1,-1))

            ##print "{0} : {1}".format(key, head_span)
            #text = allNPs[key].text
            #i = 0
            #final_text = ""
            #for ch in text:

                #if i == head_span[0]:
                    #ch = "{"+ch
                #if i == pn_span[0]:
                    #ch = "["+ch
                #if i == sc_span[0]:
                    #ch = "("+ch

                #if i == head_span[1]:
                    #ch = ch+"}"
                #if i == pn_span[1]:
                    #ch = ch+"]"
                #if i == sc_span[1]:
                    #ch = ch+")"

                #i += 1
                #final_text = final_text + ch

            #print "{0:60} => {1}".format(text, final_text)

