#!/usr/bin/python
# File Name : entry.py
# Purpose : An entry in the LKB
# Creation Date : 01-30-2013
# Last Modified : Tue 09 Apr 2013 01:59:38 PM MDT
# Created By : Nathan Gilbert
#
from collections import defaultdict
from itertools import count
from operator import itemgetter

from pyconcile import utils

class Entry:
    #classwide 
    __index = count(0)
    __sem_sources = ("SU", "WN", "ST")

    def __init__(self):
        self._text = ""
        self._head = ""

        #the total number of times this instance if found in the training docs.
        self._count = 1

        #the number of times this entity appeared in a specific document.
        self._doc_count = {}

        #unique identifier for this instance
        self._index = next(self.__index)

        #word_pairs are indexed by document then ce
        self.word_pairs = defaultdict(list)

        #these are indexed by semantic info type:
        #SUN-> Sundance domain dict
        #WN -> WordNet
        #STA -> Stanford Parser
        #Source -> ce -> semantic classes
        self.lexico_semantic = defaultdict(dict)
        self.this_semantic_tags = defaultdict(list)

    def setText(self, text, head=False):
        if head:
            self._text = utils.getReconcileHead(text)
            self._head = self._text
        else:
            self._text = text
            self._head = utils.getReconcileHead(text)

    def getText(self):
        return self._text

    def setDoc(self, doc):
        self._doc_count[doc] = self._doc_count.get(doc, 0) + 1

    def setDocCount(self, doc, count):
        self._doc_count[doc] = count

    def setSemanticTag(self, source, tag):
        self.this_semantic_tags[source].append(tag)

    def getSemanticTags(self, source):
        return self.this_semantic_tags[source]

    def updateCount(self, doc):
        self._count += 1
        self._doc_count[doc] = self._doc_count.get(doc, 0) + 1

    def getCount(self):
        return self._count

    def setCount(self, c):
        self._count = c

    def addCoref(self, doc, ce):
        self.word_pairs[doc].append(ce)

    def addSemantic(self, source, ce, semantic_class):
        if ce in list(self.lexico_semantic[source].keys()):
            self.lexico_semantic[source][ce].append(semantic_class)
        else:
            self.lexico_semantic[source][ce] = [semantic_class]

    def getAntecedentCounts(self, full_string=True):
        """
        The method will lower case all CEs before counting the individual
        strings.
        """
        counts = {}
        if full_string:
            for doc in list(self.word_pairs.keys()):
                for ce in self.word_pairs[doc]:
                    ce_clean = utils.getReconcileCleanString(ce.lower())
                    counts[ce_clean] = counts.get(ce_clean, 0) + 1
                    #counts[ce.lower()] = counts.get(ce.lower(), 0) + 1
            return counts
        else:
            for doc in list(self.word_pairs.keys()):
                for ce in self.word_pairs[doc]:
                    ce_head = utils.getReconcileHead(ce.lower())
                    counts[ce_head] = counts.get(ce_head, 0) + 1
            return counts
        return counts

    def getLexicoSemanticCounts(self, source):
        counts = {}
        for ce in list(self.lexico_semantic[source].keys()):
            for sem_cls in self.lexico_semantic[source][ce]:
                counts[sem_cls] = counts.get(sem_cls, 0) + 1
        return counts

    def getNonStringMatchLSCounts(self, source):
        counts = {}
        for ce in list(self.lexico_semantic[source].keys()):
            ce_clean = utils.getReconcileCleanString(ce.lower())
            if ce_clean == self._text:
                continue
            for sem_cls in self.lexico_semantic[source][ce]:
                counts[sem_cls] = counts.get(sem_cls, 0) + 1
        return counts

    def getNormalizedSemanticCounts(self, source):
        counts = defaultdict(dict)
        for ce in list(self.lexico_semantic[source].keys()):
            ce_clean = utils.getReconcileCleanString(ce.lower())
            for sem_cls in self.lexico_semantic[source][ce]:
                if ce_clean in list(counts.keys()):
                    counts[ce_clean][sem_cls] = counts[ce_clean].get(sem_cls, 0) + 1
                else:
                    counts[ce_clean] = {sem_cls : 1}
        return counts

    def reconcile_output(self):
        """
        Does not lower cases CEs, let Reconcile do that (or not.)
        That means some words will need to be merged in Reconcile "he" == "He", etc.
        """
        final_string = ""
        final_string += "TEXT: {0}\n".format(self._text)
        final_string += "ID: {0}\n".format(self._index)
        final_string += "Count: {0}\n".format(self._count)

        final_string += "=Doc Count Begin=\n"
        for doc in list(self._doc_count.keys()):
            final_string += "{0} $!$ {1}\n".format(doc, self._doc_count[doc])
        final_string += "=Doc Count End=\n"

        final_string += "=CEs Begin=\n"
        for doc in list(self.word_pairs.keys()):
            for ce in set(self.word_pairs[doc]):
                #format: doc $!$ ce 
                final_string += "{0} $!$ {1} $!$ {2}\n".format(doc, ce, self.word_pairs[doc].count(ce))
        final_string += "=CEs End=\n"

        final_string += "=Self Tags Begin=\n"
        for source in list(self.this_semantic_tags.keys()):
            for tag in set(self.this_semantic_tags[source]):
                final_string += "{0} $!$ {1} $!$ {2}\n".format(source, tag, self.this_semantic_tags[source].count(tag))
        final_string += "=Self Tags End=\n"

        final_string += "=Semantic Begin=\n"
        for source in list(self.lexico_semantic.keys()):
            #for some reason, I had each semantic class getting assigned the
            #same overall count?
            #sem_counts = self.getLexicoSemanticCounts(source)
            for ce in self.lexico_semantic[source]:
                for sem_cls in set(self.lexico_semantic[source][ce]):
                    c = self.lexico_semantic[source][ce].count(sem_cls)
                    final_string += "{0} $!$ {1} $!$ {2} $!$ {3}\n".format(source, ce, sem_cls, c)
        final_string += "=Semantic End=\n"
        final_string += "$!$\n"
        return final_string

    def __str__(self):
        """
        Human readable LKB
        Notes:
        1. Lower cases CEs
        """
        final_string = "#"*72 + "\n"
        final_string += "TEXT: {0}\n".format(self._text)
        final_string += "ID: {0}\n".format(self._index)
        final_string += "Count: {0}\n".format(self._count)
        final_string += "CEs =>\n"
        word_pair_counts = self.getAntecedentCounts(False)
        sorted_counts = sorted(iter(word_pair_counts.items()),
                key=itemgetter(1), reverse=True)
        for pair in sorted_counts:
            final_string += "\t{0:50} : {1}\n".format(pair[0], pair[1])
        final_string += "="*72 + "\n"

        for source in list(self.lexico_semantic.keys()):
            norm_sem_counts = self.getNormalizedSemanticCounts(source)
            #for ce in self.lexico_semantic[source]:
            for ce in list(norm_sem_counts.keys()):
                #only print out the first entry for wordnet human consumption
                if source == "WN":
                    for sem_cls in norm_sem_counts[ce]:
                        final_string += "{0} => {1:35} ({2}):{3}\n".format(source, ce, sem_cls, norm_sem_counts[ce][sem_cls])
                        break
                else:
                    for sem_cls in norm_sem_counts[ce]:
                        final_string += "{0} => {1:35} ({2}):{3}\n".format(source, ce, sem_cls, norm_sem_counts[ce][sem_cls])
        final_string += "#"*72
        final_string += "\n"
        return final_string
