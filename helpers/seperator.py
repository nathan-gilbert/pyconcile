#!/usr/bin/python
# File Name : seperator.py
# Purpose : Script to take all heuristic matches and seperate them into different annots file for easier use with multiple classifiers.
# Creation Date : 03-14-2011
# Last Modified : Fri 18 Mar 2011 10:10:02 AM MDT
# Created By : Nathan Gilbert
#
import sys
from optparse import OptionParser
from bar import ProgressBar
from collections import defaultdict

import reconcile

def outputCollapsed(filename, annots, header):
    """print the collapsed pairs"""

    outFile = open(filename,"w")
    outFile.write("#"+header+"\n")
    line = 0
    for a in annots:
        if a.attr.get("REF","") == "":
            outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t\n" % (line, a.getStart(),a.getEnd(),a.getID()))
        else:
            outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%s\"\tTYPE=\"%s\"\t\n" % (line, a.getStart(),a.getEnd(),a.getID(),a.attr["REF"],a.attr["TYPE"]))
        line +=1
    outFile.close()

def match(np1, np2):
    if np1.getText().lower() == np2.getText().lower():
        return True
    text1_tokens = np1.getText().split()
    text2_tokens = np2.getText().split()
    if text1_tokens[-1].lower() == text2_tokens[-1].lower():
        return True
    return False

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--list", dest="fileList", help="Filelist of featureDirs to process", type="string", action="store")
    parser.add_option("-o", "--out-file", dest="outfile", help="Name of file to write filelist of used docs to", type="string", action="store", default="merge")
    parser.add_option("-r", "--out-dir", dest="outdir", help="Name of dir to write filelist of used docs to", type="string", action="store", default="/home/ngilbert")
    parser.add_option("-d", "--total-docs", dest="D", help="Total # of documents to use", type="int", action="store", default=-1)
    parser.add_option("-w", help="Write Reconcile output in directories supplied by FILELIST", action="store_true", dest="write", default=False)
    #parser.add_option("-p", "--strings", help="Separate out pronoun hueristics", action="store_true", dest="write", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    fileList = open(options.fileList, 'r')
    files = filter(lambda x : not x.startswith("#"), fileList.readlines())
    stringMatchPairs = defaultdict(list)
    heuristicPairs = defaultdict(list)
    pronounPairs = defaultdict(list)
    finalPairs = defaultdict(list)

    #update the options if necessary
    if options.D > 0:
        prog = ProgressBar(options.D)
    else:
        prog = ProgressBar(len(files))
        options.D = len(files)

    sys.stdout.write("\r")
    totalDocs = 0
    print "Reading in %d files..." % (options.D)
    while (totalDocs < options.D):
        f = files.pop(0)
        if f.startswith("#"):
            continue
        f = f.strip()
        all_pairs = reconcile.getPronounPairs(f)
        for p in all_pairs:
            if match(p[0],p[1]):
                p[1].attr["TYPE"] = p[1].attr["TYPE"]+":str"
                stringMatchPairs[f].append(p)
            else:
                heuristicPairs[f].append(p)
                if p[1].attr["TYPE"].find("pronoun") > -1:
                    pronounPairs[f].append(p)
        if len(all_pairs) > 0:
            totalDocs+=1
        prog.update_time(totalDocs)
        sys.stdout.write("\r%s" % (str(prog)))
        sys.stdout.flush()
    sys.stdout.write("\r \r\n")

    #output all string match into one file.
    outList = defaultdict(list)
    if options.write:
        print "Writing files string match files..."
        for f in stringMatchPairs.keys():
            DOCUMENT=f.strip()
            outList["string"].append(int(f[f.rfind("/")+1:]))
            filename = f+"/annotations/sep_string"
            collapsedStrPairs = reconcile.collapse(stringMatchPairs[f])
            header = "this doc: %d string pairs %d docs total" % (len(collapsedStrPairs), totalDocs)
            outputCollapsed(filename, collapsedStrPairs, header)

        print "Writing files heuristic files..."
        for f in heuristicPairs.keys():
            DOCUMENT=f.strip()
            outList["heur"].append(int(f[f.rfind("/")+1:]))
            filename = f+"/annotations/sep_heuristic"
            collapsedHeurPairs = reconcile.collapse(heuristicPairs[f])
            header = "this doc: %d heuristic pairs %d docs total" % (len(collapsedHeurPairs), totalDocs)
            outputCollapsed(filename, collapsedHeurPairs, header)

        print "Writing files pronoun files..."
        for f in heuristicPairs.keys():
            DOCUMENT=f.strip()
            outList["pronoun"].append(int(f[f.rfind("/")+1:]))
            filename = f+"/annotations/sep_pronoun"
            collapsedProPairs = reconcile.collapse(pronounPairs[f])
            header = "this doc: %d heuristic pairs %d docs total" % (len(collapsedProPairs), totalDocs)
            outputCollapsed(filename, collapsedProPairs, header)

        for k in outList.keys():
            out = open(options.outdir+"/"+options.outfile+"_"+k, 'w')
            for l in outList[k]:
                out.write(str(l)+"\n")
            out.close()
