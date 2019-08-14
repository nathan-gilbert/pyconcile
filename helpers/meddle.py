#!/usr/bin/python
# Creation Date : 10/5/2010
# Last Modified : Mon 25 Apr 2011 03:51:09 PM MDT
# Created By : Nathan Gilbert
#
import sys
from optparse import OptionParser
from collections import defaultdict

from pyconcile import reconcile

def all_string_matches(nps):
    matches = defaultdict(list)
    for n in nps:
        text=n[2]["text"]
        matches[text].append(n)
    return matches

def definite_matches(nps):
    defM=defaultdict(list)
    for n in nps:
        if n[2]["definite"] == "true":
            text=n[2]["text"]
            defM[text].append(n)
    return defM

def outputMUCStyle(duncan_pairs, match_pairs):
    outFile = open("meddle","w")
    line=1
    i=0
    duncan_pairs = sorted(duncan_pairs,key=lambda p : p[0].getStart(), reverse=True)
    for p in duncan_pairs:
        antecedent = p[0]
        anaphor = p[1]
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t#DUNCAN\n" % (line,antecedent.getStart(),antecedent.getEnd(),i))
        line+=1
        i+=1
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%d\"\t#DUNCAN\n" % (line,anaphor.getStart(),anaphor.getEnd(),i,i-1))
        line+=1
        i+=1

    match_pairs= sorted(match_pairs,key=lambda p : p[0][0], reverse=True)
    for p in match_pairs:
        antecedent = p[0]
        anaphor = p[1]
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t#MEDDLE\n" % (line, antecedent[0], antecedent[1], i))
        line+=1
        i+=1
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%d\"\t#MEDDLE\n" % (line,anaphor[0],anaphor[1], i, i-1))
        line+=1
        i+=1
    outFile.close()

def outputPairStyle(duncan_pairs, match_pairs):
    outFile = open("meddle_pairs","w")
    #outFile = open("duncan_pairs","w")
    line=0
    duncan_pairs = sorted(duncan_pairs,key=lambda p : p[0].getStart(), reverse=True)
    match_pairs= sorted(match_pairs,key=lambda p : p[0][0], reverse=True)
    pair_spans = []

    for p in duncan_pairs:
        antecedent = p[0]
        anaphor = p[1]
        outFile.write("%d\t%d,%d\t%d,%d\tduncan_pair\t\n" % (line, antecedent.getStart(), antecedent.getEnd(), anaphor.getStart(), anaphor.getEnd()))
        pair_spans.append((antecedent.getStart(), antecedent.getEnd(), anaphor.getStart(), anaphor.getEnd()))
        line+=1

    for p in match_pairs:
        antecedent = p[0]
        anaphor = p[1]
        if (antecedent[0],antecedent[1],anaphor[0],anaphor[1]) not in pair_spans:
            outFile.write("%d\t%d,%d\t%d,%d\tmeddle_pair\t\n" % (line, antecedent[0], antecedent[1], anaphor[0], anaphor[1]))
            line+=1
    outFile.close()

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dir", dest="directory", help="The base directory for this file", type="string", action="store")
    parser.add_option("-n", "--duncan", dest="duncanonly",help="Only use the Duncan Heuristics, no string match, not even Duncans.", action="store_true", default=False)
    parser.add_option("-s", help="Generate new string matches", action="store_true", dest="strmatches", default=False)
    parser.add_option("-o", help="Do not remove all Duncan string matches, only duplicates", action="store_true", dest="original", default=False)
    parser.add_option("-w", help="Write Reconcile output", action="store_true", dest="write", default=False)
    parser.add_option("-v", help="Verbose. Be it.", action="store_true", dest="verbose", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    duncan_pairs = reconcile.getDuncanPairs(options.directory)

    if options.duncanonly:
        options.orginal = True

    #remove string matches from duncan files
    new_duncan_pairs = []
    for d in duncan_pairs:
        if d[0].getText() != d[1].getText():
            if options.verbose:
                print("Duncan Non-String Match ", end=' ')
                print(d[0],d[1])
            new_duncan_pairs.append(d)
        else:
            if options.verbose:
                print("Duncan String Match ", end=' ')
                print(d[0],d[1])
            if options.original:
                new_duncan_pairs.append(d)

    if options.duncanonly and options.write:
        outputPairStyle(new_duncan_pairs, [])
        sys.exit(0)

    #find all string matches in nps file.
    if options.verbose:
        print()
        print("String matches added:")

    match_pairs=[]
    if options.strmatches:
        nps=reconcile.getNPs_props(options.directory)
        strm=all_string_matches(nps)
        for s in list(strm.keys()):
            #if len(strm[s]) > 1 and strm[s][0][2]["text_lower"] != "who" and strm[s][0][2]["pronoun"] == "NONE":
            first=None
            for k in strm[s]:
                if first == None:
                    first = k
                else:
                    match_pairs.append((first,k))
            if options.verbose:
                print("%s %d" % (k[2]["text"], len(strm[s])))

    #output new duncan file, with all old annotations plus new string match ones.
    if options.write:
        outputPairStyle(new_duncan_pairs, match_pairs)
