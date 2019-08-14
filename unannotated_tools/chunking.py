#!/usr/bin/python
# File Name : chunking.py
# Purpose : Take a raw text file, and produce NP chunks.
# Creation Date : 06-21-2012
# Last Modified : Fri 13 Jul 2012 04:30:48 PM MDT
# Created By : Nathan Gilbert
#
import sys
import nltk
from nltk.corpus import brown

class Chunker:
    def __init__(self):
        """
        Constructor
        """
        self.grammar = r"""
                        NP: {<DT|CD|PP\$>?<JJ.*>*<NN.*>+}
                        """
        self.simple_chunker = nltk.RegexpParser(self.grammar)
        self.tag_patterns = [
                (r'.*ing$', 'VBG'),     #gerunds
                (r'.*ed$', 'VDB'),      #simple past
                (r'.*es$', 'VBZ'),      #3rd singular present
                (r'.*ould$', 'MD'),     #modal
                (r'.*\'s$', 'NN$'),     #possessive noun
                (r'.*s$', 'NNS'),        #plural nouns
                (r'^-?[0-9]+(.[0-9]+)?$','CD'), #cardinal numbers
                (r'.*', 'NN')           #default to noun
            ]

        #NOTE: from page 111 in nltk book
        self.tokenize_patterns = r'''
            (?x)
            ([A-Z]\.)+
            | \w+(-\w+)*
            | \$?\d+(\.\d+)?%?
            | \.\.\.
            | [][.,;"'?():-_`]
        '''

        #other taggers, trained on brown
        #self.regexp_tagger = nltk.RegexpTagger(self.tag_patterns)
        #self.unigram_tagger = nltk.UnigramTagger(brown.tagged_sents(categories='news'),
        #        backoff=self.regexp_tagger)
        #self.bigram_tagger = nltk.BigramTagger(brown.tagged_sents(categories='news'),
        #        backoff=self.unigram_tagger)

    def raw2tags(self, sentence):
        """
        Takes raw text sentence and returns the tagged sentence.
        """
        #print sentence
        tokenized_sentence = nltk.regexp_tokenize(sentence,
                self.tokenize_patterns)
        #return self.bigram_tagger.tag(tokenized_sentence)

        #NOTE using the treebank tagger
        return nltk.pos_tag(tokenized_sentence)

    def chunk(self, text):
        """
        Assumes that text is in the format:
            [(word1, tag1), (word2, tag2)...(wordn,tagn)]
        """
        return self.simple_chunker.parse(text)

