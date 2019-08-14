#!/usr/bin/python
# File Name : label_gold_from_list.py
# Purpose : Takes a list of gold annotations and a directory, labels all the
# occurrences of a member of this list in the given raw.txt file. Labels in
# Reconcile annot format 
# Creation Date : 12-14-2011
# Last Modified : Wed 14 Dec 2011 03:35:53 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile.annotation import Annotation
from pyconcile.annotation_set import AnnotationSet

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <dir> <list>" % (sys.argv[0])
        sys.exit(1)

    gList = open(sys.argv[2], 'r')
    goldText = []
    for line in gList:
        line=line.strip()
        goldText.append(line)

    annots = AnnotationSet("found gold")
    rawText = open(sys.argv[1]+"/raw.txt",'r')
    allLines = ''.join(rawText.readlines())
    rawText.close()

    i = 0
    for g_text in goldText:
        g_text = " %s " % g_text

        if allLines.find(g_text) > -1:
            start = allLines.find(g_text) + 1
            end = start + len(g_text) - 2
            text = allLines[start:end]

            attr = {"TEXT" : text}
            a = Annotation(start, end, i, attr, text)
            i+=1

            annots.add(a)

    #for a in annots:
    #    print a

    #output Reconcile file
    outfile = open(sys.argv[1]+"/annotations/gnps", 'w')
    i=0
    for a in annots:
        out = "%d\t%d,%d\tstring\tTEXT=\"%s\"\tID=\"%d\"\t\n" % (i,
                a.getStart(),a.getEnd(),a.getATTR("TEXT"), a.getID())
        outfile.write(out)
        i+=1
    outfile.close()
