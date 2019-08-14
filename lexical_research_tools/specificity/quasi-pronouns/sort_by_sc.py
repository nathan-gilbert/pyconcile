#!/usr/bin/python
# File Name : sort_by_sc.py
# Purpose :
# Creation Date : 01-06-2014
# Last Modified : Mon 06 Jan 2014 12:54:23 PM MST
# Created By : Nathan Gilbert
#
import sys
from collections import defaultdict

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <labels> <hierarchy>" % (sys.argv[0]))
        sys.exit(1)

    sorted_words = []
    with open(sys.argv[1], 'r') as labelFile:
        for line in labelFile:
            line = line.strip()
            tokens = line.split()
            word = tokens[-1].strip()
            sorted_words.append(word)

    sem2words = defaultdict(list)
    with open(sys.argv[2], 'r') as hFile:
        for line in hFile:
            line = line.strip()
            tokens = line.split()
            word = tokens[0].strip()
            sem = tokens[1]
            depth = int(tokens[2])
            max_depth = int(tokens[3])
            sem2words[sem].append(word)

    for key in list(sem2words.keys()):
        print(key)
        #sort the words in sem2words by their position in the other list.
        y = sorted(sem2words[key], key=lambda x : sorted_words.index(x))
        for word in y:
            print("\t"+word)

