#!/usr/bin/python
# File Name : wordnet_hierachy.py
# Purpose :
# Creation Date : 01-06-2014
# Last Modified : Wed 12 Feb 2014 10:47:20 AM MST
# Created By : Nathan Gilbert
#
import sys
from collections import defaultdict

import en
from nltk.corpus import wordnet as wn
from pyconcile.bar import ProgressBar

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <wordlist> <senselist>" % (sys.argv[0])
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

    MAX_DEPTH = {
           "PER" : 0,
           "ANI" : 0,
           "PLA" : 0,
           "LOC" : 0,
           "ORG" : 0,
           "BUI" : 0,
           "DIE" : 0,
           "VIR" : 0,
           "EVE" : 0,
           "VEH" : 0,
           "NUM" : 0,
           "ABS" : 0,
           "PHY" : 0
            }

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
                senses = map(int, senses)
                senselist[word].extend(senses)
            else:
                senselist[word].append(int(senses[0].replace("*","").replace("+","")))

    words2depth = {}
    words2sem   = {}
    prog = ProgressBar(len(wordlist))
    i=0
    for word in wordlist:
        prog.update_time(i)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        i+=1
        synsets = wn.synsets(word, pos=wn.NOUN)
        if len(synsets) < 1:
            singular_word = en.noun.singular(word)
            synsets = wn.synsets(singular_word, pos=wn.NOUN)

        if len(synsets) > 0:
            if "+def_wn" in sys.argv:
                #use the first two default wordnet sysnets
                if len(synsets) > 1:
                    synsets = [synsets[0], synsets[1]]
                else:
                    synsets = [synsets[0]]
            else:
                #only select the synsets we care about
                senses = senselist[word]
                new_synsets = []
                for s in senses:
                    new_synsets.append(synsets[s])
                synsets = new_synsets

            #just take the first synset...
            #synset = synsets[0]
            for synset in synsets:
                #find which of the above branches this synset is under.
                found = False
                paths = synset.hypernym_paths()
                for path in paths:
                    path.reverse()
                    #print path
                    for syn in path:
                        for key in TOPLEVELS.keys():
                            if syn == TOPLEVELS[key]:
                                sp = synset.shortest_path_distance(TOPLEVELS[key])
                                #print "{0:20} : {1:10} : {2}".format(word, key, sp)
                                if words2depth.get(word, 10**6) > sp:
                                    if MAX_DEPTH[key] < sp:
                                        MAX_DEPTH[key] = sp
                                    words2depth[word] = sp
                                    words2sem[word] = key
                                    found = True
                                    break
                        if found:
                            break
                    if found:
                        break
    sys.stderr.write("\r \r\n")
            #else:
            #    print "{0:20} : {1:10}".format(word, "Not found")
        #else:
        #    print "{0:20} : {1:10}".format(word, "None")

    #for key in MAX_DEPTH:
    #    print "{0:3} {1}".format(key, MAX_DEPTH[key])

    for word in words2depth.keys():
        print "{0:20} {1:3} {2} {3}".format(word, words2sem[word],
                words2depth[word], MAX_DEPTH[words2sem[word]])
