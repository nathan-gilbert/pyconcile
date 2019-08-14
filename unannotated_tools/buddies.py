#!/usr/bin/python
# File Name : buddies.py
# Purpose :
# Creation Date : 07-13-2012
# Last Modified : Mon 16 Jul 2012 05:29:04 PM MDT
# Created By : Nathan Gilbert
#
import sys
from collections import defaultdict

import nltk

from pyconcile import reconcile
from pyconcile import utils as py_utils
from chunking import Chunker
import utils

#Read in a test document, take stock of what pairs are present and whether or
#not they are coreferent.

#Look for these noun phrases in the unannotated documents and record:
# if (gold-X,gold-Y) appear together in the unannotated document and they are
# coreferent
# if (gold-X,gold-Z) appear together in the unannotated document and they are
# not coreferent.
# what (gold-X, np-A) appear together. i.e. what noun phrases appear with these
# gold noun phrases

class NP:
    def __init__(self):
        self.text = ""
        self.gold_buddies = []
        self.buddies = []

    def __str__(self):
        s = "{0} : [{1}]".format(self.text, ", ".join(self.gold_buddies))
        return s

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <gold-document> <unannotated-documents-list>" % (sys.argv[0])
        sys.exit(1)

    #read in gold chains
    gold_chains = reconcile.getGoldChains(sys.argv[1])
    gold_chain_text = defaultdict(list)

    pos_tags = reconcile.getPOS(sys.argv[1])
    tokens = reconcile.getTokens(sys.argv[1])

    for key in gold_chains.keys():
        for mention in gold_chains[key]:
            if mention.pprint() not in map(lambda x : x.pprint(),
                    gold_chain_text[key]):
                #np_pos = [x.getATTR("TAG") for x in \
                #        pos_tags.getOverlapping(mention)]
                #np_tok = [x.getText() for x in \
                #        tokens.getOverlapping(mention)]
                #mention.setProp("TAGS", np_pos)
                #mention.setProp("TOKENS", np_tok)
                gold_chain_text[key].append(mention)
            #print mention.pprint()
        #print "-"*25

    tracked_nps = []
    for key in gold_chain_text.keys():
        for mention in gold_chain_text[key]:
            new_np = NP()
            new_np.text = mention.pprint().strip()
            new_np.gold_buddies.extend(list(set(map(lambda x :
                x.pprint().strip(), gold_chain_text[key])) -
                set([mention.pprint().strip()])))
            tracked_nps.append(new_np)

    #for np in tracked_nps:
    #    print np
    #sys.exit(1)

    #for key in gold_chain_text.keys():
    #    for mention in gold_chain_text[key]:
    #        #print py_utils.getHead(mention)
    #        print mention.pprint()
    #    print "-"*25

    #sentence_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
    chunker = Chunker()

    #cycle through unannotated documents
    ufile =[]
    with open(sys.argv[2], 'r') as unannotated_file_list:
        ufiles = filter(lambda x : not x.startswith("#"),
                unannotated_file_list.readlines())

    #TODO: going to need to do a deeper analysis of the unannotated
    #documents..., need real POS tags and NE recognition
    for f in ufiles:
        f=f.strip()
        raw_text = ""
        with open(f+"/nathan.clean", 'r') as inFile:
            raw_text = ''.join(inFile.readlines())

        #sentences = sentence_splitter.tokenize(raw_text)
        #for sentence in sentences:
        #    sentence = sentence.replace("\n", " ")
        #    tagged_sentence = chunker.raw2tags(sentence)
        #    if tagged_sentence == []:
        #        continue
        #    np_chunks = utils.extract_phrases(chunker.chunk(tagged_sentence), "NP")
        #    for np in np_chunks:
        #        chunk_text = ' '.join(map(lambda x : x[0], np)).lower()

        #take stock of the noun phrases

