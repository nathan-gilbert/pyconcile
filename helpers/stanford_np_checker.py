#!/usr/bin/python
# File Name : stanford_np_checker.py
# Purpose :
# Creation Date : 01-28-2014
# Last Modified : Tue 28 Jan 2014 04:24:28 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    for f in files:
        f=f.strip()
        #print "Working on file {0}".format(f)
        stanford_nps = reconcile.getStanfordNPs(f)

        with open(f+"/raw.txt", 'r') as txtFile:
            allLines = ''.join(txtFile.readlines())

        for np in stanford_nps:
            head = allLines[np["HEAD_START"]:np["HEAD_END"]]
            print("{0:40} => {1} => {2}".format(np.getText(), np["HEAD"], head))

        print("="*72)
