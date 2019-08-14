#!/usr/bin/python
# File Name : inspectLinks.py
# Purpose :
# Creation Date : 11-25-2011
# Last Modified : Fri 25 Nov 2011 05:04:05 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <dir> <predictions-dir>" % (sys.argv[0]))
        sys.exit(1)

    response_pairs = reconcile.getReconcileResponsePairs(sys.argv[1],
            sys.argv[2], 1.0)

    for pair in response_pairs:
        antecedent = pair[0]
        anaphor = pair[1]

        print("%s <- %s" % (antecedent.ppprint(), anaphor.ppprint()))
