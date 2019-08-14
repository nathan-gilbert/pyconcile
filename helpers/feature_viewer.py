#!/usr/bin/python
# File Name : feature_viewer.py
# Purpose : load in features.arff file and looks at the values produced by the
# feature extractors
# Creation Date : 11-22-2011
# Last Modified : Tue 22 Nov 2011 03:29:50 PM MST
# Created By : Nathan Gilbert
#
import sys
import string
from collections import defaultdict

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <dir> <features.dir>" % (sys.argv[0]))
        sys.exit(1)

    #read in features.arff file
    featuresFile = open(sys.argv[1]+"/"+sys.argv[2]+"/features.arff", 'r')
    allLines = featuresFile.readlines()
    featureLines = [x for x in allLines if x.startswith("@ATTRIBUTE")]
    dataLines = [x for x in allLines if not x.startswith("@")]

    features_names = []
    for line in featureLines:
        line = line.replace("@ATTRIBUTE","").strip()
        tokens = list(map(string.strip, line.split("\t")))
        features_names.append(tokens[0])


    features = {}
    for line in dataLines:
        line=line.strip()
        if line == '':
            continue

        values = line.split(",")

        pair_values={}
        i = 0
        for f in features_names:
            pair_values[f] = values[i]
            i += 1

        k = "%s,%s" % (pair_values["ID1"], pair_values["ID2"])
        features[k] = pair_values

    nps = reconcile.getNPs_annots(sys.argv[1])

    for k in list(features.keys()):
        ids = list(map(int, k.split(",")))
        ante = nps.getAnnotByID(ids[0])
        ana = nps.getAnnotByID(ids[1])

        f= ' '.join(["%s=%s" % (kk, features[k][kk]) for kk in \
            sorted(features[k].keys())])

        print("%s <- %s %s" % (ante.pprint(), ana.pprint(), f))

        #if features[k]["class"] == "+":
        #    print "%s <- %s" % (ante.pprint(), ana.pprint())
