#!/usr/bin/python
# File Name : domain_common_nouns.py
# Purpose : Counts all common nouns found in a domain. 
# Creation Date : 04-26-2013
# Last Modified : Mon 29 Apr 2013 03:58:14 PM MDT
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data

class NP:
    def __init__(self, text):
        self.full_text = text
        self.head = ""
        self.count = 1
        #possibly track modifiers, possessors, semantics, etc

    def _makeHead(self):
        #TODO
        pass

    def incrementCount(self):
        self.count += 1

    def getText(self):
        return self.full_text

    def getCount(self):
        return self.count

    def __str__(self):
        final_str = "{0:3} : {1:35}".format(self.count, self.full_text)
        return final_str

#NOTE: right now, only focusing on gold mentions
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(fileList.readlines())

    propers_to_skip = []
    with open("proper_names_to_skip", 'r') as properFile:
        for line in properFile:
            if line.startswith("#"): continue
            line=line.strip()
            propers_to_skip.append(line)

    nps = {}
    for f in files:
        if f.startswith("#"): continue
        f=f.strip()
        gold_nps = reconcile.getNPs(f)

        for np in gold_nps:
            ident = utils.textClean(np.getText()).lower()

            #NOTE: skip pronouns
            if ident in data.ALL_REL:
                continue

            #NOTE: skip proper names
            if np.getATTR("contains_pn") is not None:
                if np.getATTR("contains_pn") == np.getText():
                    continue
            #NOTE: further propers to skip 
            if ident in propers_to_skip: continue
            if ident.endswith("corp."): continue
            if ident.endswith("co."): continue
            if ident.endswith("ltd."): continue
            if ident.endswith("inc."): continue
            if ident.endswith("ag"): continue
            if ident.endswith("plc"): continue

            if ident in nps.keys():
                nps[ident].incrementCount()
            else:
                new_np = NP(ident)
                nps[ident] = new_np

    #now sort them
    sorted_nps = sorted(nps.iteritems(), key=lambda x : x[1].getCount(), reverse=True)

    for np in sorted_nps:
        #np[0] -> string key
        #np[1] -> NP class instance
        print "{0:3} : {1}".format(np[1].getCount(), np[0])
        #print "{0}".format(np[0])
