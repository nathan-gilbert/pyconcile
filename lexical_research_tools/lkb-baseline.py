#!/usr/bin/python
# File Name : lkb-baseline.py
# Purpose :
# Creation Date : 02-11-2013
# Last Modified : Mon 11 Feb 2013 01:10:18 PM MST
# Created By : Nathan Gilbert
#
import sys
import os
from optparse import OptionParser

from pyconcile import feature_utils

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filelist", help="List of files to process",
            action="store", dest="filelist", type="string", default="")
    parser.add_option("-r", "--fdir", help="Feature directory",
            action="store", dest="fdir", type="string", default="")
    #parser.add_option("-b", "--baseline", help="Baselines to run",
    #        action="store", dest="baseline", type="int", default=0)
    (options, args) = parser.parse_args()

    if (len(sys.argv) < 2) or (options.filelist == ""):
        parser.print_help()
        sys.exit(1)

    files = []
    with open(options.filelist, 'r') as fileList:
        files.extend(fileList.readlines())
    baselines = ["WordPairBinary"]
    outDir="/features.lkb_baseline"
    #outFile=outDir+"/predictions.DecisionTree.muc6_DecisionTree_baseline"
    #outFile=outDir+"/predictions.DecisionTree.muc7_DecisionTree_baseline"
    outFile=outDir+"/predictions.DecisionTree.promed_DecisionTree_baseline_1"

    docNo = 0
    for f in files:
        if f.startswith("#"):
            continue
        f = f.strip()
        final_pairs = {}
        print "Working on : {0}".format(f)

        #read in the features
        features = feature_utils.getFeatures(f, options.fdir)
        for key in features.keys():
            if "WordPairBinary" in features[key].keys():
                #these are the pairs that need to be set as coref
                #print feat
                final_pairs[key] = 1.0

        #cycle over the features and select any that are positive as 
        #one that are correct

        #output the new results [union'd]
        try:
            os.mkdir(f + outDir)
            os.mkdir(f + outFile)
        except OSError:
            pass
        with open(f + outFile + "/predictions", 'w') as predictFile:
            for key in final_pairs.keys():
                predictFile.write("%d,%s %0.2f\n" % (docNo, key, final_pairs[key]))
        docNo += 1

