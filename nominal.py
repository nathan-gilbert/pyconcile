#!/usr/bin/python
# File Name : Nominal.py
# Purpose : a class to contain nominals and various statistics regarding them.
# Creation Date : 10-21-2011
# Last Modified : Mon 05 Dec 2011 10:54:23 AM MST
# Created By : Nathan Gilbert
#
import sys
import numpy

from pyconcile.annotation import Annotation
from pyconcile.annotation_set import AnnotationSet

class Nominal:
    def __init__(self):
        self.text = ""                    # the normalized text of the nominal
        self.texts = []                   # the texts are used to express this
                                          # nominal
        self.docs = {}                    # the documents this nominal is found
        self.sentence_distance = []       # sentence distances
        self.text_tile_distance = []      # tile distances
        self.doc_location = []            # what percentile in the doc is this
                                          # found.
        self.count = 0                    # the total number of times this
                                          # common noun was seen.
        self.semantic_tags = {}           # the coreferent semantic tags
        self.this_semantic = {}           # the semantic tags of this nominal
        self.prev_types = {}              # the coreferent antecedent types
        self.prev_antecedents = {}        # what are the previous antecedents?
        self.prev_anti_antecedents = {}   # what are the previous non-antecedents?
        self.duncan_anti_antecedents = {} # what are the previous
                                          # non-antecedents supplied by Duncan?
        self.context_switch_verbs = {}    # verbs that switch categories
                                          # between a non-coreferent antecedent     
                                          # and an anaphor.
        self.context_switch_adverbs = {}  # same thing, but with adverbs
        self.sundance_morph = {}          # sundance morphology
        self.sundance_role = {}           # sundance role
        self.previous_preps = {}          # the types of prepositional phrases
                                          # this nominal appears in
        self.middle_words = {}            # words between two Markables if they
                                          # are coreferent and there are no
                                          # other markables between them,

        self.list_stats = {"ANTE_SEMANTIC"     : self.semantic_tags,
                           "PREV_ANTES"        : self.prev_antecedents,
                           "PREV_ANTI_ANTES"   : self.prev_anti_antecedents,
                           "DUNCAN_ANTI_ANTES" : self.duncan_anti_antecedents,
                           "THIS_SEMANTIC"     : self.this_semantic,
                           "PREV_TYPES"        : self.prev_types,
                           "C_VERBS"           : self.context_switch_verbs,
                           "C_ADVERBS"         : self.context_switch_adverbs,
                           #"SUN_MORPH"       : self.sundance_morph,
                           #"SUN_ROLE"        : self.sundance_role,
                           "PREV_PREPS"        : self.previous_preps,
                           "MIDDLE_WORDS"      : self.middle_words
                           }

        self.attributes = {"COREF_PROB" : self._prob,
                           "EXIST_PROB" : self._prob,
                           "BA_PROB"    : self._prob,
                           "DOC_AVG"    : self._avg,
                           "TILE_AVG"   : self._avg,
                           "SENT_AVG"   : self._avg,
                           "LOC_AVG"    : self._avg
                           }
    def setText(self, t):
        self.text = t

    def addFulltext(self, ft):
        self.texts.append(ft)

    def addDoc(self, d):
        self.docs[d] = self.docs.get(d, 0) + 1

    def _prob(self, prob):
        prob = "%0.2f" % (self.attributes.get(prob + "_COUNT", 0.0) / float(self.count))
        return prob

    def _avg(self, avg):
        if avg == "DOC":
            return float(self.count) / len(self.docs)
        elif avg == "SENT":
            try:
                return float(sum(self.sentence_distance)) / \
                    len(self.sentence_distance)
            except ZeroDivisionError:
                return 0.0
        elif avg == "TILE":
            try:
                return float(sum(self.text_tile_distance)) / \
                    len(self.text_tile_distance)
            except ZeroDivisionError:
                return 0.0
        elif avg == "LOC":
            try:
                return float(sum(self.doc_location)) / \
                        len(self.doc_location)
            except ZeroDivisionError:
                #this will happen for base antecedents and existentials
                return -1.0

    def addAttribute(self, text, number):
        self.attributes[text] = number

    def updatePrevPreps(self, prep):
        if prep is not None:
            text=prep.getText().lower()
            self.previous_preps[text] = self.previous_preps.get(text, 0) + 1

    def updateIntermediateWords(self, words):
        words=words.lower()
        #if words == "":
        #    words = "$!$"
        self.middle_words[words] = self.middle_words.get(words, 0) + 1

    def updateSemanticTags(self, tag):
        """Updates the counter of previous semantic tags."""
        self.semantic_tags[tag] = self.semantic_tags.get(tag, 0) + 1

    def updateThisSemantic(self, tag):
        """Updates the counter of previous semantic tags."""
        self.this_semantic[tag] = self.this_semantic.get(tag, 0) + 1

    def updateSundanceRole(self, role):
        self.sundance_role[role] = self.sundance_role.get(role, 0) + 1

    def updateSundanceMorph(self, mor):
        self.sundance_morph[mor] = self.sundance_morph.get(mor, 0) + 1

    def updateAnteType(self, t):
        self.prev_types[t] = self.prev_types.get(t, 0) + 1

    def updatePrevAntes(self, a):
        self.prev_antecedents[a] = self.prev_antecedents.get(a, 0) + 1

    def updatePrevAntiAntes(self, a):
        self.prev_anti_antecedents[a] = self.prev_anti_antecedents.get(a, \
                0) + 1

    def updateDuncanAntiAntes(self, a):
        self.duncan_anti_antecedents[a] = self.duncan_anti_antecedents.get(a, \
                0) + 1

    def increment(self, text):
        self.attributes[text] = self.attributes.get(text, 0) + 1

    def updateSwitchVerbs(self, verb):
        self.context_switch_verbs[verb] = self.context_switch_verbs.get(verb,
                0) + 1

    def updateSwitchAdverbs(self, adverb):
        self.context_switch_adverbs[adverb] = \
        self.context_switch_adverbs.get(adverb,
                0) + 1

    def incrementCount(self):
        self.count += 1

    def __str__(self):
        features = ""
        for attr in self.attributes.keys():
            if attr.find("_PROB") > -1:
                features += "%s=%0.2f\n" % (attr,
                        float(self.attributes[attr](attr.replace("_PROB", ""))))
            elif attr.find("_AVG") > -1:
                features += "%s=%0.2f\n" % (attr,
                        float(self.attributes[attr](attr.replace("_AVG", ""))))
            else:
                features += "%s=%0.2f\n" % (attr, float(self.attributes[attr]))

        #prints out all dictionaries
        for l in self.list_stats.keys():
            tags = "{"
            for t in self.list_stats[l].keys():
                tags += "%s->%d|" % (t, self.list_stats[l][t])
            tags = tags.strip()
            if tags.endswith("|"):
                tags = tags[:-1]
            tags += "}"
            features += "%s=%s\n" % (l, tags)

        features += "TOTAL_COUNT=%d\n" % self.count
        features += "TOTAL_DOCS=%d\n" % len(self.docs.keys())

        #median sentence distance
        try:
            features += "MEDIAN_DIST=%d\n" % (numpy.median(self.sentence_distance))
        except TypeError:
            features += "MEDIAN_DIST=0\n"

        #median text tile distance
        try:
            features += "MEDIAN_TILE=%d\n" % (numpy.median(self.text_tile_distance))
        except TypeError:
            features += "MEDIAN_TILE=0\n"

        features += "MEDIAN_DOC=%d\n" % (numpy.median(self.docs.values()))
        features = features.strip()
        return "TEXT:%s\n%s" % (self.text, features)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <first-argument>" % (sys.argv[0])
        sys.exit(1)
