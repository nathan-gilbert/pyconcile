#!/usr/bin/python
# File Name : lexical_pronouns.py
# Purpose :
# Creation Date : 11-02-2012
# Last Modified : Mon 12 Nov 2012 10:27:37 AM MST
# Created By : Nathan Gilbert
#
import sys

from collections import defaultdict

from pyconcile import reconcile
from pyconcile import document

class Mention:
    def __init__(self, t):
        self.text = t
        self.count = 0
        self.antecedents = defaultdict(list)

    def add_antecedent(self, a, d):
        self.antecedents[a].append(d)

    def __str__(self):
        out_str = "{0}\n".format(self.count)
        #out_str += "[{0}]\n".format(", ".join(self.antecedents.keys()))
        tmp = []
        for key in list(self.antecedents.keys()):
            avg_dist = sum(self.antecedents[key]) / float(len(self.antecedents[key]))
            #out_str += "\t{0} : {1}\n".format(key.replace("\n", " "),
            #        avg_dist)
            tmp.append(("{0}".format(key.replace("\n", " ")), avg_dist))
        sorted_tmp = sorted(tmp, key=lambda x : x[1])
        for t in sorted_tmp:
            out_str += "\t{0} : {1}\n".format(t[0], t[1])

        return out_str

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list>" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(fileList.readlines())

    #collect these cases
    PRONOUNS = ("them", "they", "it", "their", "we", "he", "she", "her", "him")
    text2mention = {}

    for f in files:
        f=f.strip()
        if f.startswith("#"):
            continue

        print("Working on document {0}".format(f))
        #get gold mentions
        gold_chains = reconcile.getGoldChains(f)
        d = document.Document(f)

        for chain in list(gold_chains.keys()):
            prev = None
            for mention in gold_chains[chain]:
                mention_text = mention.getText().lower()
                if (mention_text in PRONOUNS) and (prev is not None):
                    if mention_text not in list(text2mention.keys()):
                        text2mention[mention_text] = \
                        Mention(mention_text)
                    prev_text = prev.getText().lower()
                    word_distance = d.word_distance(prev, mention)
                    text2mention[mention_text].count += 1
                    text2mention[mention_text].add_antecedent(prev_text,
                            word_distance)
                prev = mention

    for key in list(text2mention.keys()):
        print("{0}".format(key))
        print(text2mention[key])
