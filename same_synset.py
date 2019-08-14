#!/usr/bin/python
# File Name : same_synset.py
# Purpose : Given a list of NPs, returns lists of NPs that are in the same synset as defined by WordNet.
# Creation Date : 05-10-2011
# Last Modified : Thu 19 May 2011 03:24:07 PM MDT
# Created By : Nathan Gilbert
#
import sys

from nltk.corpus import wordnet as wn

from pyconcile import annotation
from pyconcile import string_match
from pyconcile import data
from pyconcile import utils

def getChains(nps):
    pass

def getPairs(nps):
    """ list(Annotations) -> list(tuples(Annotations), "same-synset") """

    pairs = []
    for i in range(0, len(nps) - 1):
        np1 = nps[i]
        np1_synsets = np1.getATTR("synsets")

        if np1_synsets == []:
            #get rid of pronouns, we don't need them.
            if np1.getATTR("pronoun") != "NONE":
                continue
            
            if np1.getATTR("date") != "NONE":
                continue

            #look in nltk wordnet for a synset
            head = np1.getText().split()[-1]
            np1_synsets = wn.synsets(head)

            #is the synset still empty?
            if np1_synsets == []:
                continue
            else:
                np1_synsets = np1_synsets[0].lemma_names

        for j in range(i + 1, len(nps)):
            np2 = nps[j]

            #check for string match, we don't care about those.
            if string_match.head_match(np1.getText(), np2.getText(), False):
                continue

            #get rid of pronouns, we don't need them.
            if np2.getATTR("pronoun") != "NONE":
                continue

            #get rid of dates, we don't need them either
            if np2.getATTR("date") != "NONE" or utils.isDate(np2.getText()):
                continue

            #skip if we don't have full synset info
            np2_synsets = np2.getATTR("synsets")
            if np2_synsets == []:

                #look in nltk wordnet for a synset
                head = np2.getText().split()[-1]
                np2_synsets = wn.synsets(head)

                #is the synset still empty?
                if np2_synsets == []:
                    continue
                else:
                    np2_synsets = np2_synsets[0].lemma_names

            #do the comparison of synsets
            if (np1_synsets[0] == np2_synsets[0]):
                
                if (string_match.guantlet(np1.getText(), np2.getText())):
                    continue
                
                #check for Proper Name/Person matches,they are very problematic
                if ((np1.getATTR("proper_name") == "true"
                    and np2.getATTR("proper_name") == "true")
                    and (np1_synsets[0][0]
                    in ('person', 'organization', 'location'))):
                    continue
                #elif not data.number_agreement(np1.getATTR("number"),
                #        np2.getATTR("number")):
                #    continue
                #elif not data.gender_agreement(np1.getATTR("gender"),
                #        np2.getATTR("gender")):
                #    continue
                else:
                    #print "%s <=> %s | %s" % (np1.pprint(), np2.pprint(), np1_synsets[0])
                    if np1 < np2:
                        pairs.append((np1, np2, "same-synset"))
                    else:
                        pairs.append((np1, np2, "same-synset"))
    return pairs

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <infile>" % (sys.argv[0])
        sys.exit(1)
