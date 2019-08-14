#!/usr/bin/python
# File Name : wordnet_labels.py
# Purpose : Labels NPs in a document with wordnet-based specificity rankings.
# Creation Date : 04-26-2013
# Last Modified : Fri 26 Apr 2013 01:02:29 PM MDT
# Created By : Nathan Gilbert
#
import sys
import nltk
from nltk.corpus import wordnet as wn

from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data

def get_highest_distance(synsets):
    d = -1
    for syn in synsets:
        if syn[1] > d:
            d = syn[1]
    return d

def get_color(d):
    if d == 0:
        return "FF0000"
    elif d == 1:
        return "FF6666"
    elif d == 2:
        return "FFCCCC"
    elif d == 3:
        return "CCFFFF"
    elif d == 4:
        return "66FFFF"
    else:
        return "FFFF00"
    return "FFFF00"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-dir>" % (sys.argv[0])
        sys.exit(1)

    #NOTE: assumes that the nps file will only have gold_nps in it.
    gold_nps = reconcile.getNPs(sys.argv[1])
    labels = {}
    buf = {}

    rawText = ""
    with open(sys.argv[1]+"/raw.txt", 'r') as txtFile:
        rawText = ''.join(txtFile.readlines())

    for np in gold_nps:
        #print np.ppprint()
        key = "{0}:{1}".format(np.getStart(),np.getEnd())
        #may need to get head for a lot of NPs.
        text = utils.textClean(np.getText().lower())
        if text in data.ALL_PRONOUNS:
            #if text in ("it","its","they","them","their"):
            #    labels[key] = 0
            #else:
            #    labels[key] = 1
            labels[key] = 0
            continue
        synsets = wn.synsets(text, pos=wn.NOUN)
        #print text,
        #print synsets

        if len(synsets) > 1:
            distance = synsets[0].hypernym_distances()
            d = get_highest_distance(distance)
            #print text,
            #print d
            buf[key] = d
        else:
            #assume they are proper names for now
            labels[key] = 4

    #normalize the labels
    highest = -1
    for key in buf.keys():
        if buf[key] > highest:
            highest = buf[key]

    for key in buf.keys():
        label = round((float(buf[key]) / highest) * 3)
        #overiding some of these decisions
        if label == 0:
            label = 1
        #elif label == 1:
        #    label = 2
        #elif label == 4:
        #    label = 3
        labels[key] = int(label)

    f = sys.argv[1][sys.argv[1].rfind("/")+1:]
    with open(f+"_specificity_labels.html", 'w') as outFile:
        outFile.write("<html>\n<body>\n")
        byte = 0
        for ch in rawText:
            close_text = ""
            for key in labels.keys():
                color = get_color(int(labels[key]))
                label = labels[key]
                start = int(key.split(":")[0])
                end = int(key.split(":")[1])
                if start == byte:
                    outFile.write("<font color=\"#{0}\">".format(color))
                elif end-1 == byte:
                    close_text = "</font><sub><font color=\"#000000\">"+str(label)+"</font></sub>"
            outFile.write(ch)
            if close_text != "":
                outFile.write(close_text)
                close_text=""
            byte += len(ch)
            if ch == "\n":
                outFile.write("<br />")
        outFile.write("\n</body>\n</html>\n")
