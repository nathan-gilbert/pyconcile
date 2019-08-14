#!/usr/bin/python
# File Name : ng-features.py
# Purpose :
# Creation Date : 02-19-2013
# Last Modified : Thu 14 Mar 2013 01:04:20 PM MDT
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <pairs-file>" % (sys.argv[0]))
        sys.exit(1)

    pairs = []
    total_pairs = 0
    with open(sys.argv[1], 'r') as pairsFile:
        for line in pairsFile:
            line = line.replace("Pair: ", "").strip()
            if line not in pairs:
                pairs.append(line)
            total_pairs += 1

    print("Uniq pairs: {0}".format(len(pairs)))

    feature_template = \
    "/uusoc/scratch/sollasollew/ngilbert/workspace/reconcile/src/reconcile/featureVector/individualFeature/setFeatures/NgTemplate.java"
    feature_template_lines = []
    with open(feature_template, 'r') as inFile:
        feature_template_lines.extend(inFile.readlines())
    feat_count = 0
    for pair in pairs:
        #print pair
        tokens = pair.split("<=")
        antecedent = tokens[0].strip()
        anaphor = tokens[1].strip()
        feat_name = "NgFeature" + str(feat_count)
        new_file = feature_template.replace("NgTemplate", feat_name)
        with open(new_file, 'w') as outFile:
            for line in feature_template_lines:
                if line.find("public class NgTemplate") > -1:
                    line = line.replace("NgTemplate", feat_name)
                    outFile.write(line)
                elif line.find("public NgTemplate") > -1:
                    line = line.replace("NgTemplate", feat_name)
                    outFile.write(line)
                elif line.find("private static final String ANTE_TEXT") > -1:
                    line = line.replace("REPLACE_ME", antecedent.replace("\"", "\\\"").replace("\'","\\\'"))
                    outFile.write(line)
                elif line.find("private static final String ANA_TEXT") > -1:
                    line = line.replace("REPLACE_ME", anaphor.replace("\"", "\\\"").replace("\'","\\\'"))
                    outFile.write(line)
                else:
                    outFile.write(line)
        feat_count += 1
        #if feat_count > 600:
        #    brea
    config_line = ""
    for i in range(0, feat_count):
        config_line += "FEATURE_NAMES=setFeatures.NgFeature" + str(i) + "\n"
    print(config_line)
