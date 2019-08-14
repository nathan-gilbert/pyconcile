#!/usr/bin/python
# File Name : null-hunter.py
# Purpose :
# Creation Date : 12-22-2011
# Last Modified : Thu 22 Dec 2011 11:38:14 AM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile.document import Document
from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist>" % (sys.argv[0])
        sys.exit(1)

    fList = open(sys.argv[1], 'r')
    for f in fList:
        if f.startswith("#"):
            continue
        f=f.strip()
        print "Working on document: %s" %f

        nps=reconcile.getNPs_annots(f)

        for np in nps:
            if np.getText() == "":
                print np

    fList.close()
