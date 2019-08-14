#!/usr/bin/python
# File Name : combine_sieve_results.py
# Purpose :
# Creation Date : 11-12-2013
# Last Modified : Thu 14 Nov 2013 10:51:07 AM MST
# Created By : Nathan Gilbert
#
import sys

class Word:
    def __init__(self, word, c, t):
        self.w = word
        self.count = c
        self.total = t

    def percent_correct(self):
        try:
            return float(self.count) / self.total
        except:
            return 0.0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <default> <not-default>" % (sys.argv[0])
        sys.exit(1)

    default_words = {}
    with open(sys.argv[1], 'r') as defaultFile:
        for line in defaultFile:
            line = line.strip()
            if line.startswith("="): break
            tokens = line.split(" : ")
            word = tokens[3].strip()
            total_correct = int(tokens[1].strip())
            total = int(tokens[2].strip())
            default_words[word] = (total_correct, total)

    other_words = {}
    with open(sys.argv[2], 'r') as otherFile:
        for line in otherFile:
            line = line.strip()
            if line.startswith("="): break
            tokens = line.split(" : ")
            word = tokens[3].strip()
            total_correct = int(tokens[1].strip())
            total = int(tokens[2].strip())
            other_words[word] = (total_correct, total)

    words = []
    for key in list(set(default_words.keys() + other_words.keys())):
        d_word = default_words.get(key, (0,0))
        o_word = other_words.get(key, (0,0))
        diff_correct = o_word[0] - d_word[0]
        diff_total = o_word[1] - d_word[1]
        words.append(Word(key, diff_correct, diff_total))

    s_words = sorted(words, key=lambda x : x.count, reverse=True)
    s_words = sorted(s_words, key=lambda x : x.percent_correct(), reverse=True)

    for w in s_words:
        print "{0:0.2f} | {1:3} | {2:3} | {3}".format(w.percent_correct(), w.count, w.total, w.w)
