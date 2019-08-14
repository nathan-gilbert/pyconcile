#!/usr/bin/python
# File Name : condense.py
# Purpose : Takes a Reconcile coref annots file and condenses all pairs to be in their proper chain configuration. 
# Assumptions: 1.) A NP can be in only one chain. See reconcile.py for more problems.
# Creation Date : 03-16-2011
# Last Modified : Mon 21 Mar 2011 04:04:25 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string
from optparse import OptionParser
from collections import defaultdict
from time import localtime, strftime

import reconcile

def collapse(pairs):
    """take a set of pairs of nps collect from various matching heuristics, and (tries to) collapses them all into coherent clusters"""
    #TODO: 1. There is still a problem with this method, sometimes a reference occurs twice and refer to two different
    #nps, thus a choice has to be made about which to resolved it to. Currently it's decided arbitrarily on a first come, first serve basis. 
    #TODO: 2. Cycles can be created where where two NPs refer to each other and there is no base antecedent. 
    #TODO: 3. Still allows for overlapping NPs to be put in separate clusters. Theoretically seems wrong.
    annotations = []
    new_annotations = []
    span2ids = defaultdict(list)

    for p in pairs:
        annotations.append(p[0])
        annotations.append(p[1])
        span1 = "%d:%d" % tuple(p[0].getSpan())
        span2 = "%d:%d" % tuple(p[1].getSpan())
        span2ids[span1].append(p[0])
        span2ids[span2].append(p[1])

    ref2span = defaultdict(list)
    for a in annotations:
        ref = a.getREF()
        if ref == -1:
            continue
        else:
            for span in span2ids.keys():
                if a.getID() in map(lambda x : x.getID(), span2ids[span]):
                    ref2span[ref].append(span)
    ID = 0
    for k in reconcile.sortBySpans(span2ids.keys()):
        start = int(k.split(":")[0])
        end = int(k.split(":")[1])
        new_annotations.append(reconcile.make_new_annotation(start, end, ID, span2ids[k]))
        ID += 1

    span2newids = {}
    for a in new_annotations:
        span = "%d:%d" % tuple(a.getSpan())
        span2newids[span] = a.getID()

    remove_list = []
    for a in new_annotations:
        if a.attr.get("REF", -1) > -1:
            new_ref = -1
            old_ref = a.attr["REF"]
            a.attr["OLD_REF"] = old_ref
            ref_set = set(map(int, a.attr["REF"].split(",")))
            for key in span2ids.keys():
                id_set = set(map(lambda x : x.getID(), span2ids[key]))
                #check to see if the ref set is really pointing to the same span
                if ref_set <= id_set:
                    new_ref = span2newids[key]
                elif list(ref_set)[0] in list(id_set):
                    #let's just see if the first one matches somewhere
                    new_ref = span2newids[key]
                else:
                    #just break down and see if matches anywhere
                    for i in list(ref_set):
                        if i in list(id_set):
                            new_ref = span2newids[key]
                            break
            if new_ref != -1:
                a.attr["REF"] = new_ref
            else:
                remove_list.append(a)
    for a in remove_list:
        try:
            new_annotations.remove(a)
        except ValueError:
            sys.stderr.write("Error: %s not in list! \n" % (a))
    return new_annotations


def outputCollapsed(filename, annots, header):
    """print the final collapsed pairs"""
    outFile = open(filename, "w")
    outFile.write("#" + header + "\n")
    line = 0
    for a in annots:
        if a.attr.get("REF", "") == "":
            outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t\n" % (line, a.getStart(), a.getEnd(), a.getID()))
        else:
            outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%s\"\tTYPE=\"%s\"\t\n" % (line, a.getStart(), a.getEnd(), a.getID(), a.attr["REF"], a.attr["TYPE"]))
        line += 1
    outFile.close()

def ppcollapsed(annots, header):
    print header
    line = 0
    for a in annots:
        if a.attr.get("REF", "") == "":
            print "%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t" % (line, a.getStart(), a.getEnd(), a.getID())
        else:
            print "%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%s\"\tTYPE=\"%s\"\t" % (line, a.getStart(), a.getEnd(), a.getID(), a.attr["REF"], a.attr["TYPE"])
        line += 1

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--file-list", dest="fileList", help="Filelist of featureDirs to process", type="string", action="store")
    parser.add_option("-d", "--total-docs", dest="D", help="Total # of docs to use", type="int", action="store", default= -1)
    parser.add_option("-o", "--other", dest="other", help="User specificed pair file", type="string", action="store")
    parser.add_option("-p", help="Use pronoun pairs", action="store_true", dest="pronoun", default=False)
    parser.add_option("-m", help="Use meddle pairs", action="store_true", dest="meddle", default=False)
    parser.add_option("-u", help="Use duncan pairs", action="store_true", dest="duncan", default=False)
    parser.add_option("-w", help="Write Reconcile output in directorys supplied by FILELIST", action="store_true", dest="write", default=False)
    parser.add_option("-v", help="Verbosity", action="store_true", dest="verbose", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    fileList = open(options.fileList, 'r')
    files = filter(lambda x : not x.startswith("#"), fileList.readlines())
    fileList.close()

    if options.D == -1:
        options.D = len(files)

    pairs = defaultdict(list)
    totalDocs = 0
    for f in map(string.strip, files):
        print "Working on document: %s" % f
        if options.pronoun:
            pairs[f].extend(reconcile.getPronounPairs(f))
        elif options.meddle:
            pairs[f].extend(reconcile.getMeddlePairs(f))
        elif options.duncan:
            pairs[f].extend(reconcile.getDuncanPairs(f))
        else:
            pairs[f].extend(reconcile.getOtherPairs(f, options.other))

        collapsedPairs = collapse(pairs[f])
        header = "#Document: %d, %s" % (totalDocs, strftime("%Y-%m-%d %H:%M:%S", localtime()))
        collapsedPairs = reconcile.checkCollpasedPairs(collapsedPairs)

        if options.verbose and not options.write:
            ppcollapsed(collapsedPairs, header)
        elif options.write:
            filename = f + "/annotations/condense"
            outputCollapsed(filename, collapsedPairs, header)

        totalDocs += 1
        print "Docs completed: %d <- %s" % (totalDocs, f)
        if totalDocs >= options.D:
            break
