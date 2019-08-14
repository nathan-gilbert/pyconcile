#!/usr/bin/python
# File Name : dt-pair-traversal.py
# Purpose : Supplied with a document, decision tree and np pair, follow this
# pair through the decision tree and determine it's final label. 
# Creation Date : 11-26-2011
# Last Modified : Sun 18 Mar 2012 04:33:38 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string
from optparse import OptionParser

from pyconcile import reconcile

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--directory", help="Directory of file to process",
            action="store", dest="directory", type="string", default="")
    parser.add_option("-t", "--tree-file", help="Decision Tree to process",
            action="store", dest="treefile", type="string", default="")
    parser.add_option("-f", "--feature-file", help="Feature file that tree was trained on",
            action="store", dest="featurefile", type="string", default="")
    parser.add_option("-1", "--antecedent", help="The antecedent id",
            action="store", dest="antecedent", type="int", default=-1)
    parser.add_option("-2", "--anaphor", help="The anaphor id",
            action="store", dest="anaphor", type="int", default=-1)

    (options, args) = parser.parse_args()
    if (len(sys.argv) < 2) or ((options.treefile == "") and \
            (options.featurefile == "")):
        parser.print_help()
        sys.exit(1)

    nps = reconcile.getNPs_annots(options.directory)
    antecedent = nps.getAnnotByID(options.antecedent)
    anaphor = nps.getAnnotByID(options.anaphor)

    #print antecedent.ppprint()
    #print anaphor.ppprint()

    features = reconcile.getFeatures(options.directory, options.featurefile)
    key = "%d,%d" % (options.antecedent, options.anaphor)
    pair_features = features[key]

    #for k in sorted(pair_features.keys()):
    #    print "%s = %s" % (k, str(pair_features[k]))

    #read in the tree
    treeFile = open(options.treefile, 'r')
    treeLines = filter(lambda x : x != "", map(string.strip,
        treeFile.readlines()))
    treeFile.close()
    del treeLines[0] #remove first 2 lines
    del treeLines[0]

    prev_depth = -1
    goDown = True
    path = []
    terminus = False
    for line in treeLines:
        if line.startswith("Number of Leaves") \
            or line.startswith("Size of the tree"):
            continue
        else:
            depth = line.count("|")

            if ((prev_depth < depth) and goDown) \
                    or ((prev_depth == depth) and not goDown):
                text = line.replace("|","").strip()

                tokens = map(string.strip, text.split())
                feat = tokens[0]
                op = tokens[1]
                value = tokens[2]
                if (value.find(":") > -1):
                    #we've found a terminus
                    value = float(value.replace(":", ""))
                    label = tokens[3]
                    stats = tokens[4]
                    terminus = True
                else:
                    value = float(tokens[2])

                if pair_features.get(feat) == value:
                    #go down this path
                    if terminus:
                        #print "%s=%d (%s)" % (feat, value, label)
                        path.append("%s=%s (%s)" % (feat, value, label))
                        break
                    else:
                        #print "%s=%d" % (feat, value)
                        path.append("%s=%s" % (feat, value))
                    goDown = True
                else:
                    terminus = False
                    goDown = False
                prev_depth = depth

    print " %s <- %s" % (antecedent.ppprint(), anaphor.ppprint())
    print " \n -> ".join(path)

