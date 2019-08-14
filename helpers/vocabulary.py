#!/usr/bin/python
# File Name : vocabulary.py
# Purpose : Generate the gold vocabulary list
# Creation Date : 01-08-2012
# Last Modified : Sun 08 Jan 2012 06:17:48 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <first-argument>" % (sys.argv[0]))
        sys.exit(1)

    V = []
    fList = open(sys.argv[1], 'r')
    for f in fList:
        f=f.strip()
        if f.startswith("#"):
            continue

        gold_annots = reconcile.parseGoldAnnots(f, True)

        for g in gold_annots:
            text = g.getText().replace("\n","").replace("\r", "")
            if text in data.ALL_PRONOUNS:
                continue
            if text not in V:
                V.append(text)

    for v in V:
        print("\"%s\"," % v)

