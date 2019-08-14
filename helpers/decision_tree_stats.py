#!/usr/bin/python
# File Name : decision_tree_stats.py
# Purpose : Gather useful information about using the Decision Tree classifier
# in Reconcile.
# Creation Date : 08-20-2012
# Last Modified : Tue 21 Aug 2012 12:47:29 PM MDT
# Created By : Nathan Gilbert
#
#DONE: how many resolutions are being made?
#DONE: what are the most common paths in the DT for positive examples (and
#      negative examples, for both training and testing.)
#DONE: the type of resolutions, (how many pronouns, common nouns, etc are being
#      resolved.)
#DONE: keep track of the resolutions that are made in a format easily read into
#      other programs (ie a python pickle)
import sys
import operator
import string

import dt_utils
from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <filelist> <treefile>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files = filter(lambda x : not x.startswith("#"), fileList.readlines())

    treeLines = []
    with open(sys.argv[2], 'r') as treeFile:
        treeLines = filter(lambda x : x != "", map(string.strip,
            treeFile.readlines()))
        del treeLines[0] #remove first 2 lines
        del treeLines[0]

    positive_res = 0
    negative_res = 0
    np_type = {"PRO" : 0, "NOM" : 0, "PRP": 0, "DAT": 0}
    pos_pairs = {} #NOTE text1:text2 ??
    pos_paths = {}
    neg_paths = {}

    for f in files:
        f = f.strip()
        print "Working on document: {0}".format(f)
        features_file = "/features.goldnps_ana_ant_propensity"

        rpairs = \
        "/predictions.DecisionTree.muc7_DecisionTree_goldnps_ana_ant_propensity"
        pairs = reconcile.getAllResponsePairs(f,features_file+rpairs)
        features = reconcile.getFeatures(f, features_file)
        nps = reconcile.getNPs_annots(f)

        #print len(pairs)
        for pair in pairs:
            feature_key = "{0},{1}".format(pair[0].getID(), pair[1].getID())
            pair_features = features[feature_key]

            #get the path in the decision tree
            path = " -> ".join(dt_utils.find_path(pair_features, treeLines))
            #print "PATH: {0}".format(path)
            if path.endswith("+"):
                pos_paths[path] = pos_paths.get(path, 0) + 1
            else:
                neg_paths[path] = neg_paths.get(path, 0) + 1

            #determine if pos or neg label
            if path.endswith("+"):
                positive_res += 1
                #keep track of the pair
                pp = pair[0].getATTR("TEXT_CLEAN")+":"+pair[1].getATTR("TEXT_CLEAN")
                pos_pairs[pp] = pos_pairs.get(pp, 0) + 1

                #determine what type of np the anaphor is
                if pair[1].getATTR("is_pronoun"):
                    np_type["PRO"] = np_type.get("PRO", 0) + 1
                elif pair[1].getATTR("is_proper"):
                    np_type["PRP"] = np_type.get("PRP", 0) + 1
                elif pair[1].getATTR("is_date"):
                    np_type["DAT"] = np_type.get("DAT", 0) + 1
                else:
                    np_type["NOM"] = np_type.get("NOM", 0) + 1
            else:
                negative_res += 1

    print "{0}/{1}/{2}".format(positive_res, negative_res,
           positive_res+negative_res)
    print "NOMS:{0} PRO:{1} PRP:{2} DAT:{3}".format(np_type["NOM"],
           np_type["PRO"], np_type["PRP"], np_type["DAT"])

    sorted_pos_paths = sorted(pos_paths.iteritems(), key=operator.itemgetter(1),
            reverse=True)
    sorted_neg_paths = sorted(neg_paths.iteritems(), key=operator.itemgetter(1),
            reverse=True)

    for x in range(10):
       print "{0} : {1}".format(sorted_pos_paths[x][0], sorted_pos_paths[x][1])
       print "-"*72
    print
    for x in range(10):
       print "{0} : {1}".format(sorted_neg_paths[x][0], sorted_neg_paths[x][1])
       print "-"*72

    print "="*72
    sorted_pairs = sorted(pos_pairs.iteritems(), key=operator.itemgetter(1),
            reverse=True)
    for x in range(50):
        print "{0}".format(sorted_pairs[x])


