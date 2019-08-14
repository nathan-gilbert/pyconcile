#!/usr/bin/python
# File Name : dt_utils.py
# Purpose :
# Creation Date : 08-20-2012
# Last Modified : Tue 21 Aug 2012 11:36:57 AM MDT
# Created By : Nathan Gilbert
#
import sys
import string

def find_path(pair_features, treeLines):
    """ returns the path in the decision tree for this pair """
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
                        path.append("+")
                        break
                    elif terminus and pair_label == "-":
                        path.append("-")
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
                        path.append("+")
                        break
                    elif terminus and pair_label == "-":
                        path.append("+")
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
                        path.append("+")
                        break
                    elif terminus and pair_label == "-":
                        path.append("-")
                        break
                else:
                    stay_at_depth = True
                    if terminus:
                        terminus = False
            else:
                print "Unknown operator %s"  % feature_operator
            prev_depth = depth
    return path
