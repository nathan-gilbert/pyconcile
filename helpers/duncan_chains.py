#!/usr/bin/python
# File Name : duncan_chains.py
# Purpose : A file to merge all duncan-related chains (automatically generated
#           coreferent pairs)
# Creation Date : 12-02-2011
# Last Modified : Fri 02 Dec 2011 04:24:41 PM MST
# Created By : Nathan Gilbert
#
import sys
from optparse import OptionParser

from pyconcile import duncan
from pyconcile.union_find import UnionFind

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file", help="File to process",
            action="store", dest="in_file", type="string", default="")
    parser.add_option("-p", "--pronouns", help="Add in pronouns [TODO]",
            action="store_true", dest="pronouns", default=False)
    parser.add_option("-s", "--string-match", help="Add in greedy string match [TODO]",
            action="store_true", dest="string_match", default=False)
    parser.add_option("-c", "--commons", help="Add in common nouns [TODO]",
            action="store_true", dest="common_nouns", default=False)
    parser.add_option("-e", "--extras", help="Add in extra resolutions [TODO]",
            action="store_true", dest="extras", default=False)
    parser.add_option("-w", "--write", help="Write out merged annotations [TODO]",
            action="store_true", dest="write", default=False)
    parser.add_option("-o", "--out-file", help="File to write annotations in [TODO]",
            action="store", dest="out_file", default="./merged")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    duncan_chains = duncan.getDuncanChains(options.in_file)
    for c in duncan_chains.keys():
        print "%d" % c
        for mention in duncan_chains[c]:
            print "  %s" % mention.ppprint()
        print



