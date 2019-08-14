#!/usr/bin/python
# File Name : vp.py
# Purpose : Virtual Pronoun class
# Creation Date : 06-12-2013
# Last Modified : Thu 20 Feb 2014 09:57:56 AM MST
# Created By : Nathan Gilbert
#
import sys
import nltk

class QuasiPronoun:
    def __init__(self, h):
        #basic
        self.head = h
        self.texts = []
        self.annotated_count = 0
        self.unannotated_count = 0
        self.annotated_docs = {}
        self.unannotated_docs = {}
        self.chains = [] #doc:ch_id

        #antecedents
        self.most_recent_antecedents = []
        self.all_entities    = []
        self.all_entities_heads    = []
        self.string_matches  = 0
        self.subj_ante       = 0
        self.dobj_ante       = 0
        self.prp_ante        = 0
        self.ante_is_mod     = 0 #the closest antecedent is modifying another
                                 #noun
        self.pro_ante        = 0
        self.nom_ante        = 0
        self.largest_chain   = 0  #TODO it was in the largest chain in doc
                                  #[i.e. focus of discourse]
        self.chain_size      = {}
        self.chain_coverage  = {} #doc to coverage % of doc
        self.nom_chain_only  = {} #chain_id to boolean

        #distances
        self.zero_sentence        = 0
        self.one_sentence         = 0
        self.two_sentence         = 0
        self.three_sentence       = 0
        self.sent_distances       = []
        self.large_distance       = 0
        self.mention_distance     = 0
        self.mention_interference = 0

        #this
        self.has_antecedent = 0
        self.starts_chain  = 0
        self.bdef_starts_chain  = 0
        self.subj          = 0
        self.dobj          = 0
        self.iobj          = 0
        self.tf_idf        = 0.0
        self.bare_definite = 0
        self.definite      = 0
        self.indefinite    = 0
        self.ind_no_app    = 0
        self.singleton     = 0
        self.appos_gov     = 0
        self.appos_dep     = 0
        self.agent         = 0
        self.adj_mod       = 0
        self.adv_mod       = 0
        self.nn_mod        = 0
        self.num_mod       = 0
        self.poss_mod      = 0
        self.is_poss       = 0
        self.prep_mod      = 0
        self.rc_mod        = 0
        self.prp_mod       = 0
        self.nom_mod       = 0
        self.one_premod    = 0 ## of times with at least one premodification
        self.faux_ba       = 0 #the number of indefinite mentions that 
                               #start the chain and are not in appositives
        self.first_clause  = 0
        self.isa           = 0
        self.hasa          = 0

        #wn
        self.h_depth     = 1.0 #the wordnet hierachy depth 
        self.wn_children = 0   #the number of instances and children

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
        self.agent_verbs         = []

    def totalDocs(self):
        return len(list(self.annotated_docs.keys())) + len(list(self.unannotated_docs.keys()))

    def updateCount(self, annotated=True):
        if annotated:
            self.annotated_count += 1
        else:
            self.unannotated_count += 1

    def totalCount(self):
        return self.annotated_count + self.unannotated_count

    def updateDocs(self, d, annotated=True):
        if annotated:
            self.annotated_docs[d] = self.annotated_docs.get(d, 0) + 1
        else:
            self.unannotated_docs[d] = self.unannotated_docs.get(d, 0) + 1

    def less_than_three(self):
        lt3 = 0
        for sd in self.sent_distances:
            if sd <= 3:
                lt3+= 1
        try:
            return float(lt3) / self.has_antecedent
        except:
            return 0.0

    def productivity(self):
        return len(list(set(self.most_recent_antecedents)))

    def productivity(self):
        try:
            #return float(len(list(set(map(lambda x : x.lower(), self.all_entities))))) / len(self.all_entities)
            #return float(len(list(set(map(lambda x : x.lower(),
            #    self.all_entities_heads))))) / len(self.all_entities_heads)
            return float(len(list(set([x.lower() for x in self.all_entities_heads])))) / len(list(self.annotated_docs.keys()))
        except:
            return 0.0

    def diversity(self):
        try:
            return float(len(list(set([x.lower() for x in self.all_entities_heads])))) / len(self.all_entities_heads)
        except:
            return 0.0

    def average_edit_distance(self):
        l = []
        for text in self.all_entities_heads:
            text = text.lower()
            l.append(nltk.edit_distance(self.head, text))
        try:
            return float(sum(l)) / len(l)
        except:
            return 0.0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <first-argument>" % (sys.argv[0]))
        sys.exit(1)

