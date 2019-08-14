#!/usr/bin/python
# File Name : vp.py
# Purpose : Virtual Pronoun class
# Creation Date : 06-12-2013
# Last Modified : Thu 18 Jul 2013 02:36:50 PM MDT
# Created By : Nathan Gilbert
#
import sys

class VirtualPronoun:
    def __init__(self, t):
        #basic
        self.text = t
        self.count = 1
        self.docs = {}
        self.chains = [] #doc:ch_id

        #antecedents
        self.most_recent_antecedents = []
        self.all_entities    = []
        self.string_matches  = 0
        self.subj_ante       = 0
        self.dobj_ante       = 0
        self.prp_ante        = 0
        self.pro_ante        = 0
        self.nom_ante        = 0
        self.largest_chain   = 0  #TODO it was in the largest chain
        self.chain_size      = {} 
        self.chain_coverage  = {} #doc to coverage % of doc
        self.nom_chain_only  = {} #chain_id to boolean

        #distances
        self.zero_sentence   = 0
        self.one_sentence    = 0
        self.two_sentence    = 0
        self.three_sentence  = 0
        self.large_distance  = 0
        self.mention_distance= 0

        #this
        self.starts_chain  = 0
        self.subj          = 0
        self.dobj          = 0
        self.tf_idf        = 0.0
        self.bare_definite = 0
        self.indefinite    = 0

        #modifiers
        self.adjective_modifiers = []
        self.common_modifiers    = []
        self.proper_modifiers    = []
        self.other_modifiers     = []
        self.of_attachments      = []
        self.on_attachments      = []
        self.by_attachments      = []
        self.which_attachments   = []
        self.with_attachments    = []
        self.that_attachments    = []
        self.verbed              = []
        self.verbing             = []

    def updateCount(self):
        self.count += 1

    def updateDocs(self, d):
        self.docs[d] = self.docs.get(d, 0) + 1

    def sentence_distance(self, sd):
        if sd == 0:
            self.zero_sentence += 1
        elif sd == 1:
            self.one_sentence += 1
        elif sd == 2:
            self.two_sentence += 1
        elif sd == 3:
            self.three_sentence += 1
        else:
            self.large_distance += 1

    def productivity(self):
        return len(set(self.most_recent_antecedents))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <first-argument>" % (sys.argv[0]))
        sys.exit(1)

