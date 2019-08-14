#!/usr/bin/python
# File Name : text_tiler.py
# Purpose : Script to process a raw.txt document with the TextTiling agorithm
# and produce a Reconcile annot file.
# Creation Date : 09-30-2011
# Last Modified : Tue 04 Dec 2012 01:43:51 PM MST
# Created By : Nathan Gilbert
#
import sys

import nltk

from pyconcile import reconcile
from pyconcile.annotation_set import AnnotationSet
from pyconcile.annotation import Annotation

#TODO there is still some data sets that do not separate sentences with
# newlines. Several docs in ACE03, need to take this into account, otherwise
# the tendency is to lump everything in one tile.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist>" % (sys.argv[0])
        sys.exit(1)

    files=[]
    with open(sys.argv[1], 'r') as fileList:
        files.extend(fileList.readlines())

    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        #read in the raw.txt file
        rawTextFile = open(f+"/raw.txt", 'r')
        rawText = ''.join(rawTextFile.readlines())
        rawTextFile.close()

        tiles = AnnotationSet("tiles")
        tiler = nltk.tokenize.TextTilingTokenizer()
        try:
            tokens = tiler.tokenize(rawText)

            for t in tokens:
                start = rawText.find(t)
                end = start + len(t)
                props = {}
                t_annot = Annotation(start, end, tokens.index(t), props, t)
                tiles.add(t_annot)
        except ValueError:
            #let's try splitting this into paragraphs on our own
            sents = reconcile.getSentences(f)
            text2start = {}
            padded_text = ""
            for s in sents:
                padded_text += s.getText() + "\n"
                text2start[s.getText()] = s.getStart()
            #tokens = [rawText]
            try:
                tokens = tiler.tokenize(padded_text)
                i = 0
                for t in tokens:
                    text = t.split("\n")
                    unpadded = ""
                    first = True
                    for t in text:
                        t = t.strip()
                        if t == "":
                            continue
                        unpadded += t + "\n"

                        if first:
                            start = rawText.find(t)
                            first = False
                    end = start + len(unpadded)
                    props = {}
                    t_annot = Annotation(start, end, i, props, unpadded)
                    i+=1
                    tiles.add(t_annot)
            except:
                tokens = [rawText]
                for t in tokens:
                    start = rawText.find(t)
                    end = start + len(t)
                    props = {}
                    t_annot = Annotation(start, end, tokens.index(t), props, t)
                    tiles.add(t_annot)
        i = 1
        out = open(f+"/annotations/tiles", 'w')
        for t in tiles:
            out.write("%d\t%d,%d\tstring\ttext_tiler\ttile=\"%d\"\t\n" % (i, t.getStart(),
                    t.getEnd(), i-1))
            i+=1
        out.close()
