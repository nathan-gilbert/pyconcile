#!/usr/bin/python
# File Name : set_feature_maker.py
# Purpose :
# Creation Date : 12-05-2012
# Last Modified : Tue 19 Feb 2013 08:11:17 PM MST
# Created By : Nathan Gilbert
#
import sys
import string

import lkb_lib
from entry import Entry

def make_wordpair(lkb):
    feature_template = "/uusoc/scratch/sollasollew/ngilbert/workspace/reconcile/src/reconcile/featureVector/individualFeature/setFeatures/SetTemplate.java"
    feature_template_lines = []
    with open(feature_template, 'r') as inFile:
        feature_template_lines.extend(inFile.readlines())
    feat_count = 0
    for entry in lkb.keys():
        if lkb[entry].getCount() < 2:
            continue
        feat_name = "Feature" + str(feat_count)
        new_file = feature_template.replace("SetTemplate", feat_name)
        with open(new_file, 'w') as outFile:
            for line in feature_template_lines:
                if line.find("public class SetTemplate") > -1:
                    line = line.replace("SetTemplate", feat_name)
                    outFile.write(line)
                elif line.find("public SetTemplate") > -1:
                    line = line.replace("SetTemplate", feat_name)
                    outFile.write(line)
                elif line.find("private static final String[] ANTECEDENTS") > -1:
                    #gather all the antecedents here.
                    antecedents = map(string.strip,
                            lkb[entry].getAntecedentCounts().keys())
                    antecedents = map(lambda x : x.replace("\"","\\\""), antecedents)
                    antecedents = map(lambda x : x.replace("\'","\\\'"), antecedents)
                    antecedents = filter(lambda x : x != "", antecedents)
                    antecedent_str = ", ".join(map(lambda x : "\"{0}\"".format(x), antecedents))
                    line = line.replace("\"REPLACE_ME\"", antecedent_str)
                    outFile.write(line)
                elif line.find("private static final String THIS_TEXT") > -1:
                    line = line.replace("REPLACE_ME", lkb[entry].getText().replace("\"", "\\\"").replace("\'","\\\'"))
                    outFile.write(line)
                else:
                    outFile.write(line)
        feat_count += 1
        #if feat_count > 600:
        #    brea
    config_line = ""
    for i in range(0, feat_count):
        config_line += "FEATURE_NAMES=setFeatures.Feature" + str(i) + "\n"
    print config_line

def make_ss(lkb):
    feature_template =\
    "/uusoc/scratch/sollasollew/ngilbert/workspace/reconcile/src/reconcile/featureVector/individualFeature/setFeatures/SundanceSetSemantic.java"
    feature_template_lines = []
    with open(feature_template, 'r') as inFile:
        feature_template_lines.extend(inFile.readlines())
    feat_count = 0
    for entry in lkb.keys():
        if lkb[entry].getCount() < 2:
            continue
        feat_name = "SunFeature" + str(feat_count)
        new_file = feature_template.replace("SundanceSetSemantic", feat_name)
        with open(new_file, 'w') as outFile:
            for line in feature_template_lines:
                if line.find("public class SundanceSetSemantic") > -1:
                    line = line.replace("SundanceSetSemantic", feat_name)
                    outFile.write(line)
                elif line.find("public SundanceSetSemantic") > -1:
                    line = line.replace("SundanceSetSemantic", feat_name)
                    outFile.write(line)
                elif line.find("private static final String[] SEM_CLASSES") > -1:
                    #gather all the antecedents here.
                    nes = lkb[entry].getLexicoSemanticCounts("SU").keys()
                    nes2 = lkb[entry].getSemanticTags("SU")
                    for ne in nes2:
                        if ne not in nes:
                            nes.append(ne)
                    nes = ", ".join(map(lambda x : "\"{0}\"".format(x), nes))
                    line = line.replace("\"REPLACE_ME\"", nes)
                    outFile.write(line)
                elif line.find("private static final String THIS_TEXT") > -1:
                    line = line.replace("REPLACE_ME", lkb[entry].getText().replace("\"", "\\\"").replace("\'","\\\'"))
                    outFile.write(line)
                else:
                    outFile.write(line)
        feat_count += 1
        #if feat_count > 600:
        #    brea
    config_line = ""
    for i in range(0, feat_count):
        config_line += "FEATURE_NAMES=setFeatures.SunFeature" + str(i) + "\n"
    print config_line

def make_wn(lkb):
    feature_template = \
    "/uusoc/scratch/sollasollew/ngilbert/workspace/reconcile/src/reconcile/featureVector/individualFeature/setFeatures/SetSemantic.java"
    feature_template_lines = []
    with open(feature_template, 'r') as inFile:
        feature_template_lines.extend(inFile.readlines())
    feat_count = 0
    for entry in lkb.keys():
        if lkb[entry].getCount() < 2:
            continue
        feat_name = "WNFeature" + str(feat_count)
        new_file = feature_template.replace("SetSemantic", feat_name)
        with open(new_file, 'w') as outFile:
            for line in feature_template_lines:
                if line.find("public class SetSemantic") > -1:
                    line = line.replace("SetSemantic", feat_name)
                    outFile.write(line)
                elif line.find("public SetSemantic") > -1:
                    line = line.replace("SetSemantic", feat_name)
                    outFile.write(line)
                elif line.find("private static final String[] SEM_CLASSES") > -1:
                    #gather all the antecedents here.
                    nes = lkb[entry].getLexicoSemanticCounts("WN").keys()
                    #nes2 = lkb[entry].getSemanticTags("WN")
                    #for ne in nes2:
                    #    if ne not in nes:
                    #        nes.append(ne)
                    nes = ", ".join(map(lambda x : "\"{0}\"".format(x), nes))
                    line = line.replace("\"REPLACE_ME\"", nes)
                    outFile.write(line)
                elif line.find("private static final String THIS_TEXT") > -1:
                    line = line.replace("REPLACE_ME", lkb[entry].getText().replace("\"", "\\\"").replace("\'","\\\'"))
                    outFile.write(line)
                else:
                    outFile.write(line)
        feat_count += 1
        #if feat_count > 600:
        #    break
    config_line = ""
    for i in range(0, feat_count):
        config_line += "FEATURE_NAMES=setFeatures.WNFeature" + str(i) + "\n"
    print config_line

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <lkb-file> +ss +wn" % (sys.argv[0])
        sys.exit(1)

    #read in the lkb
    lkb = lkb_lib.read_in_lkb(sys.argv[1])

    if "+ss" in sys.argv:
        make_ss(lkb)
    elif "+wn" in sys.argv:
        make_wn(lkb)
    else:
        make_wordpair(lkb)
