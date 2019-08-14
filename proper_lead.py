#!/usr/bin/python
# File Name : proper_lead.py
# Purpose :
# Creation Date : 05-11-2011
# Last Modified : Thu 19 May 2011 06:46:59 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string

from nltk.corpus import wordnet as wn

from pyconcile import annotation
from pyconcile import string_match
from pyconcile import data

def getPairs(nps):
    """ list(Annotations) -> list(tuples(Annotations), "proper-lead") """

    pairs = []
    for i in range(0, len(nps)-1):
        np1=nps[i]

        #we don't need pronouns
        if np1.getATTR("pronoun") != "NONE":
            continue

        if np1.getATTR("indefinite") == "true":
                continue

        pn_text1 = np1.getPNText().strip()
        if pn_text1 == "":
            continue

        mods1 = np1.getATTR("modifier")
        mod_head1 = string_match.getHead(mods1)

        #need to enforce the rule that the head is a Proper Noun.
        if not string_match.isHead(np1.getText(), pn_text1):
            continue

        for j in range(i+1,len(nps)):
            np2=nps[j]

            #let's throw away everything but definite NPs
            if np2.getATTR("definite") != "true":
                continue

            #we don't need pronouns
            if np2.getATTR("pronoun") != "NONE":
                continue

            #let's not deal with proper names either, our goal is common nouns
            if np2.getATTR("proper_name") == "true":
                continue

            pn_text2 = np2.getPNText()
            head2 = string_match.getHead(np2.getText())
            mods2 = np2.getATTR("modifier")
            mod_head2 = string_match.getHead(mods2)
            
            #check the criteria for a match here.
            if string_match.word_overlap(head2, mods1, False):
                if np1 < np2:
                    pairs.append((np1,np2,"proper-lead"))
                else:
                    pairs.append((np1,np2,"proper-lead"))
    return pairs

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(("Usage: %s <first-argument>" % (sys.argv[0])))
        sys.exit(1)


