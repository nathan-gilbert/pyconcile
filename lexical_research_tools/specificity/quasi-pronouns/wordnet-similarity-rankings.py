#!/usr/bin/python
# File Name : wordnet_similarity_rankings.py
# Purpose :
# Creation Date : 02-11-2014
# Last Modified : Tue 11 Feb 2014 04:22:56 PM MST
# Created By : Nathan Gilbert
#
import sys
from nltk.corpus import wordnet as wn
from collections import defaultdict

import en
from pyconcile.bar import ProgressBar

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <wordlist> <senselist> <hierachy>" % (sys.argv[0]))
        sys.exit(1)

    TOPLEVELS = {
           "PER" : wn.synset('person.n.01'),
           "ANI" : wn.synset('animal.n.01'),
           "PLA" : wn.synset('plant.n.02'),
           "LOC" : wn.synset('location.n.01'),
           "ORG" : wn.synset('group.n.01'),
           "BUI" : wn.synset('building.n.01'),
           "DIE" : wn.synset('illness.n.01'),
           "VIR" : wn.synset('organism.n.01'),
           "EVE" : wn.synset('event.n.01'),
           "VEH" : wn.synset('vehicle.n.01'),
           "NUM" : wn.synset('number.n.01'),
           "ABS" : wn.synset('abstraction.n.01'),
           "PHY" : wn.synset('object.n.01')
           }

    wordlist = []
    with open(sys.argv[1], 'r') as wordList:
        wordlist.extend([x.strip() for x in wordList.readlines()])

    senselist = defaultdict(list)
    with open(sys.argv[2], 'r') as wnSenseList:
        for line in wnSenseList:
            line = line.strip()
            tokens = line.split("\t")
            word = tokens[0].strip()
            senses = tokens[1].split(",")
            if len(senses) > 1:
                senses = list(map(int, senses))
                senselist[word].extend(senses)
            else:
                senselist[word].append(int(senses[0].replace("*","").replace("+","")))

    hierachy = {}
    word2sem = {}
    with open(sys.argv[3], 'r') as hList:
        for line in hList:
            tokens = line.split()
            word = tokens[0].strip()
            sem = tokens[1].strip()
            depth = int(tokens[2])
            max_depth = int(tokens[3])
            try:
                hierachy[word] = float(depth) / max_depth
            except:
                hierachy[word] = 1.0

            word2sem[word] = sem

    for word in wordlist:
        #get the right synset
        synsets = wn.synsets(word, pos=wn.NOUN)
        if len(synsets) < 1:
            singular_head = en.noun.singular(word)
            synsets = wn.synsets(singular_head, pos=wn.NOUN)

        #find the right semantic class to pull from.
        sem=word2sem.get(word, None)
        if sem is None:
            continue

        if len(synsets) > 0:
            senses = senselist[word]
            new_synsets = []
            for s in senses:
                new_synsets.append(synsets[int(s)])
            synsets = new_synsets

        #find the wordnet similarity based on these two pieces of info.
        path_based_sim = TOPLEVELS[sem].path_similarity(synsets[0])
        lch_sim = TOPLEVELS[sem].lch_similarity(synsets[0])
        print("{0:3}\t{1:>0.4f}\t{2:>0.4f}\t{3}".format(sem, path_based_sim, lch_sim, word))

        #TODO sort by semantic class, sort by the proper order (where the
        #top-level of the semantic class are at the top and so on.)
