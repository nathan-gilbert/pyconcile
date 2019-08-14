#!/usr/bin/python
# File Name : wordnet_labels2.py
# Purpose :
# Creation Date : 12-16-2013
# Last Modified : Wed 12 Feb 2014 10:57:01 AM MST
# Created By : Nathan Gilbert
#
import sys
import operator
import math
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data
from pyconcile.annotation_set import AnnotationSet
from pyconcile.bar import ProgressBar

import specificity_utils
import en
from nltk.corpus import wordnet as wn

class Head:
    def __init__(self, h):
        self.head = h
        self.shortest_depth = -1
        self.senses = -1
        self.senses_below = -1
        self.avg_depth = -1.0
        self.avg_min_depth = -1.0
        self.hyponym_count = 0
        self.instance_count = 0
        self.concrete = -1.0
        self.h_depth_perc = 1.0
        self.child_perc   = 0.0

    def criteria(self):
        if self.senses == -1:
            return 0.0

        if self.h_depth_perc == 0:
            self.h_depth_perc = 0.01

        #old way
        #return ((self.h_depth_perc)**-1) * (1.0 / (self.avg_min_depth + 1)) * math.log(self.instance_count+self.hyponym_count+1)
        return ((self.h_depth_perc)**-1) * math.log(self.instance_count+self.hyponym_count+1)

def avg_depth(head_synset):
    if head_synset is None:
        return -1.0
    try:
        hypernym_paths = head_synset.hypernym_paths()
        total = 0
        for p in hypernym_paths:
            total += len(p)
        #return float(head_synset.max_depth() + head_synset.min_depth()) / len(head_synset.hypernyms())
        return float(total) / len(hypernym_paths)
    except:
        return -1.0

def hyponym_closure(head_synset):
    if head_synset is None:
        return -1
    hyp = lambda x : x.hyponyms()
    return len(list(head_synset.closure(hyp)))

def hyponym_closure2(synset):
    if synset is None:
        return None
    hyp = lambda x : x.hyponyms()
    return list(synset.closure(hyp))

def wordnet_specificity(head_synset):
    if head_synset is None:
        return -1
    return head_synset.shortest_path_distance(wn.synset("entity.n.01"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <wordlist> <senses_list> <hierachy>" % (sys.argv[0])
        sys.exit(1)

    head_dict = {}

    wordlist = []
    with open(sys.argv[1], 'r') as wordList:
        wordlist.extend(map(lambda x : x.strip(), wordList.readlines()))

    senselist = defaultdict(list)
    with open(sys.argv[2], 'r') as wnSenseList:
        for line in wnSenseList:
            line = line.strip()
            tokens = line.split("\t")
            word = tokens[0].strip()
            senses = tokens[1].split(",")
            if len(senses) > 1:
                senselist[word].extend(senses)
            else:
                senselist[word].append(senses[0].replace("*","").replace("+",""))

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
    hierachy["entity"] = 0.01

    prog = ProgressBar(len(wordlist))
    i=0
    sem2mostchild = {}
    for word in wordlist:
        prog.update_time(i)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        i+=1

        singular_head = en.noun.singular(word)
        head_dict[word] = Head(word)
        synsets = wn.synsets(word, pos=wn.NOUN)

        concrete = specificity_utils.getNounConcreteness(word)
        if concrete < 0:
            concrete = specificity_utils.getNounConcreteness(singular_head)
        head_dict[word].concrete = concrete

        if len(synsets) < 1:
            synsets = wn.synsets(singular_head, pos=wn.NOUN)
            #hypernyms = en.noun.hypernyms(singular_head, sense=0)

        if len(synsets) > 0:
            if "+def_wn" in sys.argv:
                #use the first two default wordnet sysnets
                if len(synsets) > 1:
                    synsets = [synsets[0], synsets[1]]
                else:
                    synsets = [synsets[0]]
            else:
                #select only select the synsets we care about
                senses = senselist[word]
                new_synsets = []
                for s in senses:
                    new_synsets.append(synsets[int(s)])
                synsets = new_synsets

            min_depth_sum = 0
            hypos = 0
            typesOfInstances = []
            for synset in synsets:
                min_depth_sum += synset.min_depth()
                if word == "entity":
                    hypos = 10**6
                    head_dict[word].hyponym_count = 10**6
                else:
                    #these are the synsets of hyponyms
                    hypos += hyponym_closure(synset)

                    #these are the instances
                    for instance in synset.instance_hyponyms():
                        new_instance = instance.lemma_names
                        #print new_instance
                        if new_instance not in typesOfInstances:
                            typesOfInstances.append(new_instance)

                    for s in hyponym_closure2(synset):
                        for instance in s.instance_hyponyms():
                            new_instance = instance.lemma_names
                            #print new_instance
                            if new_instance not in typesOfInstances:
                                typesOfInstances.append(new_instance)

            if word == "entity":
                head_dict[word].instance_count = 10**6
            else:
                head_dict[word].instance_count = len(typesOfInstances)

            head_dict[word].hyponym_count = hypos

            total_children = head_dict[word].instance_count + head_dict[word].hyponym_count
            if total_children > sem2mostchild.get(word2sem.get(word, 'PHY'), 0):
                if word not in word2sem.keys():
                    print "#Semantics not found for {0}".format(word)
                sem2mostchild[word2sem.get(word, 'PHY')] = total_children

            head_dict[word].avg_min_depth = float(min_depth_sum) / len(synsets)

            head_dict[word].senses = len(synsets)
            head_synset = synsets[0]
            head_dict[word].h_depth_perc = hierachy.get(word, 1.0)

    sys.stderr.write("\r \r\n")
    #sorted_keys = sorted(head_dict.keys())
    #sorted_values = sorted(head_dict.values(), key=lambda x : x.hyponym_count,
    #        reverse=True)
    sorted_values = sorted(head_dict.values(), key=lambda x : x.criteria(),
            reverse=True)
    #for head in sorted_keys:
    print "{0:>6} {1:>6} {2}".format(
            "chil", "hier", "head"
            )
    for noun in sorted_values:
        if noun.senses < 0:
            continue

        if noun.head != "entity":
            num = float(noun.instance_count + noun.hyponym_count)
            try:
                child_perc = num / sem2mostchild.get(word2sem.get(noun.head, "PHY"), num)
            except:
                child_perc = 1.0
        else:
            child_perc = 1.0

        print "{0:>6.2f} {1:>6.2f} {2}".format(
                child_perc,           #0
                noun.h_depth_perc,    #1
                noun.head             #2
                )
