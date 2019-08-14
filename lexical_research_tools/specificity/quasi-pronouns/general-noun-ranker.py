#!/usr/bin/python
# File Name : general-noun-ranker.py
# Purpose :
# Creation Date : 02-26-2014
# Last Modified : Thu 27 Feb 2014 02:04:18 PM MST
# Created By : Nathan Gilbert
#
import sys

from collections import defaultdict

class Noun:
    def __init__(self):
        self.head = None
        self.sem = None
        self.chil = 0.0
        self.depth = 0.0
        self.wn1 = 0.0
        self.wn2 = 0.0
        self.amd = 0.0
        self.hsa = 0.0
        self.app = 0.0
        self.count = 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <wordlist> <*.wn.labels> <*.sim> <*.gen>" % (sys.argv[0])
        sys.exit(1)

    DATASET="MUC4"
    #DATASET="MUC6"
    #DATASET="PROMED"
    TOP_N = 20
    wordlist = []
    word2noun = {}
    with open(sys.argv[1], 'r') as wordList:
        wordlist.extend(map(lambda x : x.strip(), wordList.readlines()))

    for word in wordlist:
        w = Noun()
        w.head = word
        word2noun[word] = w

    with open(sys.argv[2], 'r') as wnLabels:
        first = True
        for line in wnLabels:
            if first:
                first = False
                continue
            tokens = line.split()
            word = tokens[2].strip()
            if word in wordlist:
                chil = float(tokens[0].strip())
                depth = float(tokens[1].strip())
                word2noun[word].chil = chil
                word2noun[word].depth = depth

    with open(sys.argv[3], 'r') as simLabels:
        first = True
        for line in simLabels:
            if first:
                first = False
                continue
            tokens = line.split()
            word = tokens[3].strip()
            if word in wordlist:
                sem = tokens[0].strip()
                if sem == "VIR":
                    sem = "DIE"
                wn1 = float(tokens[1])
                wn2 = float(tokens[2])

                word2noun[word].sem = sem
                word2noun[word].wn1 = wn1
                word2noun[word].wn2 = wn2

    with open(sys.argv[4], 'r') as genLabels:
        first = True
        for line in genLabels:
            if first:
                first = False
                continue
            tokens = line.split()
            word = tokens[4].strip()
            if word in wordlist:
                count = int(tokens[0])
                amd = float(tokens[1])
                hsa = float(tokens[2])
                app = float(tokens[3])

                word2noun[word].count = count
                word2noun[word].amd = amd
                word2noun[word].hsa = hsa
                word2noun[word].app = app

    semantic_class_rank = defaultdict(list)
    for word in word2noun.keys():
        if word2noun[word].sem is not None:
            semantic_class_rank[word2noun[word].sem].append(word)

    sorted_sem_keys = sorted(semantic_class_rank.keys())
    sorted_lists = {}

    word_ranks = defaultdict(list)
    final_qps = []

    #rank on criteria 1
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count, reverse=True)
        s_list = sorted(s_list, key=lambda x : word2noun[x].chil, reverse=True)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria1", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i, word2noun[word].chil,
                            word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on criteria 2
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : word2noun[x].depth)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria2", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                            word2noun[word].depth, word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on criteria 3
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : word2noun[x].wn1)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria3", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                            word2noun[word].wn1, word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on criteria 4
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : word2noun[x].wn2)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria4", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                            word2noun[word].wn2, word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on criteria 5
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : word2noun[x].amd, reverse=True)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria5", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                            word2noun[word].amd, word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on criteria 6
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : word2noun[x].hsa, reverse=True)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria6", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                            word2noun[word].hsa, word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on criteria 7
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : word2noun[x].app, reverse=True)
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria7", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i <= TOP_N:
                    s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                            word2noun[word].app, word2noun[word].head)
                    outFile.write(s)
                word_ranks[word].append(i)
                i += 1

    #rank on all
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : (float(sum(word_ranks[x])) / 7))
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria_avg", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i > TOP_N:
                    break
                s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                        (float(sum(word_ranks[word])) / 7), word2noun[word].head)
                i += 1
                outFile.write(s)

    #rank on all
    for sem in semantic_class_rank.keys():
        s_list = sorted(semantic_class_rank[sem], key=lambda x : word2noun[x].count)
        s_list = sorted(s_list, key=lambda x : min(word_ranks[x]))
        sorted_lists[sem] = s_list

    with open(DATASET + ".criteria_min", 'w') as outFile:
        for key in sorted_sem_keys:
            outFile.write("-"*72 + "\n")
            i = 1
            for word in sorted_lists[key]:
                if i > TOP_N:
                    break
                s = "{0:3} {1:>2} {2:>4.2f} : {3}\n".format(key, i,
                        min(word_ranks[word]), word2noun[word].head)
                final_qps.append(word)
                i += 1
                outFile.write(s)


    with open(DATASET+".qps", 'w') as outFile:
        for qp in final_qps:
            outFile.write("{0}\n".format(qp))
