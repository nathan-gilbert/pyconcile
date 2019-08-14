#!/usr/bin/python
# File Name : annotation_writer.py
# Purpose : methods to handle the output of an annotation set.
# Creation Date : 05-03-2012
# Last Modified : Thu 21 Mar 2013 10:58:27 AM MDT
# Created By : Nathan Gilbert
def write_annotations(dest, annots, name):
    """
       dest : where to write the annotations
       annots: the annotations to write
       name: the name of the annotations
    """
    outFile = open(dest+"/"+name, 'w')
    i = 0
    for a in annots:
        out_str = "%d\t%d,%d\tstring\tID=\"%d\"\t%s\n" % \
        (i,a.getStart(),a.getEnd(),a.getID(),a.getProps2String())
        outFile.write(out_str)
        i+=1
    outFile.close()

def write_nps(dest, annots):
    with open(dest, 'w') as outFile:
        i = 0
        for a in annots:
            out_str = "%d\t%d,%d\tstring\tNP\tID=\"%d\"\t%s\n" % \
            (i,a.getStart(),a.getEnd(),a.getID(),a.getProps2String())
            outFile.write(out_str)
            i+=1
