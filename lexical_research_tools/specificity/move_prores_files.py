#!/usr/bin/python
# File Name : move_prores_files.py
# Purpose :
# Creation Date : 11-18-2013
# Last Modified : Mon 02 Dec 2013 01:58:07 PM MST
# Created By : Nathan Gilbert
#
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <filelist> [-hobbs/-rap] <experiment>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    if sys.argv[2] == "-hobbs":
        FILE_TYPE = "hobbs"
    else:
        FILE_TYPE = "rap"

    EXP = sys.argv[3]
    for f in files:
        f=f.strip()
        print "Working on file: {0}".format(f)
        os.rename(f+"/annotations/"+FILE_TYPE,
                f+"/annotations/"+FILE_TYPE+"_"+EXP)
        #os.rename(f+"/annotations/"+FILE_TYPE+"_"+EXP,
        #        f+"/annotations/"+FILE_TYPE)
