#!/usr/bin/python
# File Name : feature-usage-stats.py
# Purpose : Tracks the usage of various stats given a specific decision tree
# model.
# Creation Date : 03-18-2012
# Last Modified : Mon 19 Mar 2012 02:39:29 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string
import operator

from pyconcile import reconcile
from pyconcile import feature_utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <corpus_dir> <prediction_dir> <filelist> <tree_file>" % (sys.argv[0]))
        sys.exit(1)

    tree_file = sys.argv[4]
    threshold=1.0
    predictions=sys.argv[2]
    feature_dir = "features.goldnps"
    data_dir = sys.argv[1]
    files = []
    with open(sys.argv[3], 'r') as filelist:
        files = list(map(string.strip, filelist.readlines()))

    all_paths = {}
    total_positive_pairs = 0
    #get all the positive pairs...
    for f in files:
        print("Processing file: %s" % f)
        positive_pairs = reconcile.getResponsePairs(data_dir+f,
                predictions, threshold)

        total_positive_pairs += len(positive_pairs)

        #NOTE features only stores the non-zero values in a vector
        features = feature_utils.getFeatures(data_dir+f, feature_dir)

        for pair in positive_pairs:
            key = "%d,%d" % (pair[0].getID(), pair[1].getID())
            #print key
            pair_features = features[key]

            #find their paths in the decision tree
            path = feature_utils.get_dt_path(pair_features, tree_file)
            str_path = '->'.join(path)
            #print str_path
            all_paths[str_path] = all_paths.get(str_path, 0) + 1

    #collect the statistics on the most used paths, etc.
    print("Total correct paths: %d" % len(list(all_paths.keys())))
    sorted_all_paths = sorted(iter(all_paths.items()),
            key=operator.itemgetter(1), reverse=True)
    #print sorted_all_paths

    print("Total positive pairs: %d" % total_positive_pairs)
    for i in range(20):
        print("%s -> %d" % (sorted_all_paths[i][0], sorted_all_paths[i][1]))

