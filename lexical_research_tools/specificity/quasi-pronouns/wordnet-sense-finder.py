#!/usr/bin/python
# File Name : wordnet_sense_finder.py
# Purpose :
# Creation Date : 12-27-2013
# Last Modified : Wed 29 Jan 2014 02:38:40 PM MST
# Created By : Nathan Gilbert
#
import sys
import string
import operator
from collections import defaultdict

import specificity_utils
import en
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from pyconcile.bar import ProgressBar

def hyponym_closure(synset):
    if synset is None:
        return None
    hyp = lambda x : x.hyponyms()
    return list(synset.closure(hyp))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist> <wordlist>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"), fileList.readlines()))

    ROOT = "/home/ngilbert/xspace/data/"
    docs = []
    for f in files:
        f=f.strip()
        f=f.replace(ROOT, "")
        docs.append(f+"/raw.txt")
    corpus = PlaintextCorpusReader(ROOT, docs)
    #sys.stderr.write(str(corpus.fileids())+"\n")
    unigrams = [token.lower() for token in corpus.words()]
    unigram_fd = nltk.FreqDist(unigrams)
    bigrams = nltk.bigrams(map(string.lower, corpus.words()))
    #sys.stderr.write(str(len(bigrams)))
    bigram_fd = nltk.FreqDist(bigrams)
    #print bigram_fd
    #print bigram_fd[("the", "emotional")]
    #print unigram_fd["the"]
    #print bigrams
    sys.stderr.write(">>>finished counting unigrams and bigrams\n")

    wordlist = []
    with open(sys.argv[2], 'r') as wordList:
        wordlist.extend(map(lambda x : x.strip(), wordList.readlines()))

    #process the documents, find the documents where each of these words
    #appear.
    words2docs = defaultdict(list)
    words2senses = defaultdict(list)

    #TODO only cycle over the documents and count words in those documents that contain
    #this word.

    #cycle over the words
    prog = ProgressBar(len(wordlist))
    j=0
    for word in wordlist:
        prog.update_time(j)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        j+=1
        word = word.strip()
        if word not in words2senses.keys():
            #print "="*70
            #print word
            synsets = wn.synsets(word, pos=wn.NOUN)
            if len(synsets) < 1:
                singular_head = en.noun.singular(word)
                synsets = wn.synsets(singular_head, pos=wn.NOUN)

            #if it only has one sense, then use that.
            if len(synsets) == 1:
                words2senses[word].append(str(0)+"+")
            elif len(synsets) > 1:
                #if more than one sense, then we must rank them.
                #collect the hyponyms [this is a smaller list than instances...]
                #collect the instance hyponyms
                #cycle over the senses, grab their children and glosses
                i = 0 #the sense #
                sense2count = {} #the sense/uni--bigram overlap
                for synset in synsets:
                    #print "-"*70
                    #hyponyms = synset.hyponyms()
                    #print "hyponyms:"
                    #print hyponyms
                    #print "all hyponyms:"
                    all_hyponyms = hyponym_closure(synset)
                    all_hyponym_words = []
                    for hyp in all_hyponyms:
                        if hyp.name not in all_hyponym_words:
                            n = hyp.name[:hyp.name.find(".")]
                            all_hyponym_words.append(n)

                    hypo_count = 0
                    for hw in all_hyponym_words:
                        tokens = hw.split("_")
                        #print tokens
                        if len(tokens) == 1:
                            hypo_count = unigram_fd[tokens[0].lower()]
                        elif len(tokens) == 2:
                            hypo_count = bigram_fd[(tokens[0].lower(),tokens[1].lower())]

                    #typesOfHyponyms = list(set([w for s in hyponym_closure(synset) for w in s.lemma_names]))
                    #typesOfInstances = synset.lemma_names
                    typesOfInstances = []
                    for s in hyponym_closure(synset):
                        for instance in s.lemma_names:
                            new_instance = instance.split("_")
                            #print new_instance
                            if new_instance not in typesOfInstances:
                                typesOfInstances.append(new_instance)

                    #print typesOfInstances
                    instance_count = 0
                    for toi in typesOfInstances:
                        #print toi
                        if len(toi) == 1:
                            instance_count += unigram_fd[toi[0].lower()]
                        elif len(toi) == 2:
                            instance_count += bigram_fd[(toi[0].lower(),toi[1].lower())]

                    #type bigrams are separated by underscores commercial_bank
                    #print typesOfSynsets
                    #print "Sense {0} hypos: {1} instances {2}".format(i,
                    #        hypo_count, instance_count)
                    total = hypo_count + instance_count
                    sense2count[str(i)] = total
                    i+= 1

                #if there were no matches, go with the first sense
                if all(v == 0 for v in sense2count.values()):
                    words2senses[word].append(str(0)+"*")
                else:
                    sorted_s2c = sorted(sense2count.iteritems(), key=operator.itemgetter(1), reverse=True)
                    words2senses[word].append(str(sorted_s2c[0][0]))

                    #if the second sense is greater than 5, add it in as well.
                    if sorted_s2c[1][1] > 5:
                        words2senses[word].append(str(sorted_s2c[1][0]))
            else:
                #don't have any synsets to work with.
                pass
    sys.stderr.write("\r \r\n")

    #output word -> sense lists (top 2)
    for word in words2senses:
        print "{0:20}\t{1}".format(word, ", ".join(words2senses[word]))
