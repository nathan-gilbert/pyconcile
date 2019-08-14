#!/usr/bin/python
# File Name : feature_utils.py
# Purpose : Utilities for accessing feature files
# Creation Date : 11-26-2011
# Last Modified : Thu 14 Mar 2013 03:17:58 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string
import gzip

import reconcile

default_features = ("DocNo", "ID1", "ID2", "SoonStr", "ProStr", "ProComp",
"PNStr_I", "PNStr_C", "PNStr_D", "WordsStr", "WordOverlap", "Modifier",
"PNSubstr_I", "PNSubstr_C", "PNSubstr_D", "WordsSubstr", "Pronoun1",
"Pronoun2", "Definite1", "Definite2", "Demonstrative2", "Embedded1",
"Embedded2", "InQuote1", "InQuote2", "BothProperNouns_I", "BothProperNouns_C",
"BothProperNouns_D", "BothEmbedded_I", "BothEmbedded_C", "BothEmbedded_D",
"BothInQuotes_I", "BothInQuotes_C", "BothInQuotes_D", "BothPronouns_I",
"BothPronouns_C", "BothPronouns_D", "BothSubjects_I", "BothSubjects_C",
"BothSubjects_D", "Subject1", "Subject2", "Appositive", "MaximalNP",
"Animacy_I", "Animacy_C", "Animacy_D", "Gender_I", "Gender_C", "Gender_S",
"Gender_D", "Number_I", "Number_C", "Number_D", "SentNum", "ParNum", "Alias",
"IAntes", "Span", "Binding", "Contraindices", "Syntax", "ClosestComp",
"Indefinite", "Indefinite1", "Prednom", "Pronoun", "ContainsPN", "Constraints",
"ProperNoun", "Agreement_I", "Agreement_C", "Agreement_D", "ProperName",
"WordNetClass_I", "WordNetClass_C", "WordNetClass_D", "WordNetDist",
"WordNetSense", "Subclass", "AlwaysCompatible", "RuleResolve", "SameSentence",
"ConsecutiveSentences", "WNSynonyms", "Quantity", "ProResolve",
"SameParagraph", "HeadMatch", "PairType_nn", "PairType_np", "PairType_nd",
"PairType_ni", "PairType_pn", "PairType_pp", "PairType_pd", "PairType_pi",
"PairType_dn", "PairType_dp", "PairType_dd", "PairType_di", "PairType_in",
"PairType_ip", "PairType_id", "PairType_ii")

def getFeatures(datadir, feature_dir,toGet=("all")):
    """
    @param datadir: the base dir for this data file
    @param feature_dir: which feature directory to read from
    @param toGet: what features to extract?
    """
    try:
        featuresFile = open(datadir+"/"+feature_dir+"/features.arff", 'r')
    except:
        try:
            import os
            import subprocess
            from cStringIO import StringIO
            p = subprocess.Popen(["zcat", os.path.join(datadir+"/"+feature_dir+"/",
                "features.arff.gz")], stdout=subprocess.PIPE)
            featuresFile = StringIO(p.communicate()[0])
        except:
            print "Features file note found"

    feature_names = []
    features = {}
    for line in featuresFile:
        line = line.strip()
        if line.startswith("@ATTRIBUTE"):
            line = line.replace("@ATTRIBUTE","").strip()
            tokens = map(string.strip, line.split("\t"))
            feature_names.append(tokens[0])
        elif line.startswith("@") or line == "":
            continue
        else:
            #print line
            values = line.split(",")
            pair_values={}
            i = 0
            for f in feature_names:
                if f in ("class", "ID1", "ID2"):
                    pair_values[f] = values[i]
                else:
                    #only store the non-zero values duh...
                    if (f in toGet) or ("all" in toGet):
                        if float(values[i]) > 0:
                            pair_values[f] = float(values[i])
                i += 1
            k = "%s,%s" % (pair_values["ID1"], pair_values["ID2"])
            features[k] = pair_values
    featuresFile.close()
    return features

def getFeatures2(datadir, feature_dir):
    """
        Input: datadir, feature_dir
        Output: features dict index by 'ante,ana' ids string
    """
    try:
        featuresFile = open(datadir+"/"+feature_dir+"/features.arff", 'r')
    except:
        #try opening a gzip file...
        featuresFile = gzip.open(datadir+"/"+feature_dir+"/features.arff.gz", 'r')

    allLines = featuresFile.readlines()
    featureLines = filter(lambda x : x.startswith("@ATTRIBUTE"), allLines)
    dataLines = filter(lambda x : not x.startswith("@"), allLines)
    featuresFile.close()

    features_names = []
    for line in featureLines:
        line = line.replace("@ATTRIBUTE","").strip()
        tokens = map(string.strip, line.split("\t"))
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
            if f in ("class", "ID1", "ID2"):
                pair_values[f] = values[i]
            else:
                pair_values[f] = float(values[i])
            i += 1

        k = "%s,%s" % (pair_values["ID1"], pair_values["ID2"])
        features[k] = pair_values
    return features

def getPairFeatures(ant, ana, features):
    """Takes in the ant and ana IDs and returns a dictonary containing this
    pair's feature values """
    #nps=reconcile.getNPs_annots(sys.argv[1])
    #antecedent = nps.getAnnotByID(ant)
    #anaphor = nps.getAnnotByID(ana)

    key = "%d,%d" % (ant, ana)
    f= ' '.join(["%s=%s" % (kk, features[key][kk]) for kk in \
        sorted(features[key].keys())])
    return f
    #print "%s <- %s %s" % (ante.pprint(), ana.pprint(), f)
    #if features[k]["class"] == "+":
    #    print "%s <- %s" % (ante.pprint(), ana.pprint())

def convert_reconcile_to_weka_name(fname):
    """
    Return the weka name for a positive instance of this feature. (if
    possible.)

    @param fname: the generic Reconcile name for this feature.
    """
    if fname in default_features:
        return fname
    elif fname+"_C" in default_features:
            return fname+"_C"
    else:
        return None
    return None

def feature_name_to_bool(fname, fkey, features):
    """
    Takes a generic feature name as found in a Reconcile config file and
    returns the name used in the actual weka arff file, returning the name used
    for a "positive" instance.

    @param fname: the general name of the feature
    @param fkey: the pair to return the proper feature
    @param features: the features dictionary
    """
    wname = convert_reconcile_to_weka_name(fname)
    if wname is None:
        return False

    if fkey in features.keys():
        if features[fkey].get(wname, 0.0) > 0:
            return True
    return False

def get_dt_path(pair_features, tree_file):
    """
    Returns a list containing the path followed by positive marked coreference
    pairs.
    """
    #read in the tree
    treeFile = open(tree_file, 'r')
    treeLines = filter(lambda x : x != '', map(string.strip,
        treeFile.readlines()))
    treeFile.close()
    del treeLines[0] #remove first 2 lines
    del treeLines[0]

    path = []
    terminus = False
    prev_depth = -1
    stay_at_depth = False
    pair_label = "-"
    for line in treeLines:
        if line.startswith("Number of Leaves") \
        or line.startswith("Size of the tree"):
            continue
        else:
            depth = line.count("|")
            line = line.replace("|","").strip()

            if stay_at_depth and (prev_depth != depth):
                continue

            tokens = map(string.strip, line.split())
            feature_name = tokens[0]
            feature_operator = tokens[1]
            feature_value = tokens[2]

            if feature_value.find(":") > -1:
                terminus = True
                feature_value = feature_value.replace(":","")
                pair_label = tokens[3]

            feature_value = float(feature_value)

            #print "%s %s %s" % (feature_name, feature_operator, feature_value)

            if feature_name in pair_features.keys():
                #this means we have a non-zero instance
                pair_value = float(pair_features[feature_name])
            else:
                pair_value = 0.0

            if feature_operator == "=":
                if pair_value == feature_value:
                    #then follow this thread...
                    #print "Matching value found: %s == %f" % (feature_name,
                    #        feature_value)
                    stay_at_depth = False
                    if feature_value != 0.0:
                        path.append(feature_name+"_Y")
                    else:
                        path.append(feature_name+"_N")

                    if terminus and pair_label == "+":
                    #    print "Correct path: ",
                    #    print "<-".join(path)
                        break
                else:
                    stay_at_depth = True
                    if terminus:
                        terminus = False
            elif feature_operator == "<=":
                if pair_value <= feature_value:
                    #print "Matching value found: %s <= %f" % (feature_name,
                    #        feature_value)
                    stay_at_depth = False
                    if feature_value != 0.0:
                        path.append(feature_name+"_Y")
                    else:
                        path.append(feature_name+"_N")

                    if terminus and pair_label == "+":
                        break
                else:
                    stay_at_depth = True
                    if terminus:
                        terminus = False
            elif feature_operator == ">":
                if pair_value > feature_value:
                    #print "Matching value found: %s <= %f" % (feature_name,
                    #        feature_value)
                    stay_at_depth = False
                    if feature_value != 0.0:
                        path.append(feature_name+"_Y")
                    else:
                        path.append(feature_name+"_N")
                    if terminus and pair_label == "+":
                        break
                else:
                    stay_at_depth = True
                    if terminus:
                        terminus = False
            else:
                print "Unknown operator %s"  % feature_operator
            prev_depth = depth
    return path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <first-argument>" % (sys.argv[0])
        sys.exit(1)

