#!/usr/bin/python
# File Name : leveling.py
# Purpose : Created a training set comprised of a specified number of specific types of training instances. 
# Creation Date : 03-01-2011
# Last Modified : Mon 25 Apr 2011 03:51:36 PM MDT
# Created By : Nathan Gilbert
#
import sys
import string
from optparse import OptionParser
from collections import defaultdict
from math import ceil,floor
from random import sample

from pyconcile import reconcile
from pyconcile.annotation import Annotation
from pyconcile.bar import ProgressBar

DOCUMENT=""

def countPairs(chains):
    total=0
    for c in chains:
        n=len(c)
        total+= n*(n-1)/2
    return total

def output(filename, pairs,header):
    outFile = open(filename,"w")
    outFile.write("#"+header+"\n")
    line=1
    i=0
    pairs = sorted(pairs, key=lambda p : p[0].getStart())
    for p in pairs:
        antecedent = p[0]
        anaphor = p[1]
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\t\n" % (line,antecedent.getStart(),antecedent.getEnd(),i))
        line+=1
        i+=1
        outFile.write("%d\t%d,%d\tstring\tCOREF\tID=\"%d\"\tREF=\"%d\"\t%s\n" % (line,anaphor.getStart(),anaphor.getEnd(),i,i-1,anaphor.attr.get("TYPE","")))
        line+=1
        i+=1
    outFile.close()

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

def sortSpans(spans):
    s = sorted(spans, key=lambda x : int(x.split(":")[1]))
    return sorted(s, key=lambda x : int(x.split(":")[0]))

def make_new_annotation(start, end, ident, annots):
    global DOCUMENT
    new = Annotation(start,end,ident, {}, "")
    #sanity check on the text
    textSet = set(map(string.strip, list(map(string.lower, [x.getText() for x in annots]))))
    if len(textSet) > 1:
        sys.stderr.write("Error: Strings don't match. %s\n" % DOCUMENT)

    new.setText(annots[0].getText())
    attr = {}
    attr["ID"] = ident
    for a in annots:
        if attr.get("OLD_ID", "") == "":
            attr["OLD_ID"] = str(a.getID())
        else:
            attr["OLD_ID"] = attr["OLD_ID"] + "," + str(a.getID())

        for key in list(a.attr.keys()):
            if attr.get(key, "") == "":
                attr[key] = a.attr[key]
            else:
                if key != "MIN":
                    if key == "TYPE":
                        attr[key] = attr[key] + "|" + a.attr[key]
                    else:
                        attr[key] = attr[key] + "," + a.attr[key]
                else:
                    if (attr[key] != a.attr[key]):
                        sys.stderr.write("Error: MINs don't match. %s\n" % DOCUMENT)
    new.setATTR(attr)
    return new

def collapse(pairs):
    """take a set of pairs of nps, and collapse them all into clusters"""
    global DOCUMENT
    annotations = []
    new_annotations = []
    span2ids = defaultdict(list)

    for p in pairs:
        annotations.append(p[0])
        annotations.append(p[1])
        span1 = "%d:%d" % tuple(p[0].getSpan())
        span2 = "%d:%d" % tuple(p[1].getSpan())
        #span2ids[span1].append(p[0].getID())
        #span2ids[span2].append(p[1].getID())
        span2ids[span1].append(p[0])
        span2ids[span2].append(p[1])

    ref2span = defaultdict(list)
    for a in annotations:
        ref = a.getREF()
        if ref == -1:
            continue
        else:
            for span in list(span2ids.keys()):
                if a.getID() in [x.getID() for x in span2ids[span]]:
                    ref2span[ref].append(span)

    ID = 0
    for k in sortSpans(list(span2ids.keys())):
        #print "%s : %s" % (k, ' '.join(map(str, sorted(map(lambda x : x.getID(), span2ids[k])))))
        start = int(k.split(":")[0])
        end = int(k.split(":")[1])
        new_annotations.append(make_new_annotation(start, end, ID, span2ids[k]))
        ID+=1

    span2newids = {}
    for a in new_annotations:
        span = "%d:%d" % tuple(a.getSpan())
        span2newids[span] = a.getID()

    remove_list=[]
    for a in new_annotations:
        if a.attr.get("REF",-1) > -1:
            new_ref = -1
            old_ref = a.attr["REF"]
            a.attr["OLD_REF"] = old_ref
            ref_set = set(map(int, a.attr["REF"].split(",")))
            for key in list(span2ids.keys()):
                id_set = set([x.getID() for x in span2ids[key]])

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
                #sys.stderr.write("Error: new REF not found! %s \n" % DOCUMENT)
                #print a

    #for k in sorted(ref2span.keys(), key=lambda x : int(x)):
    #    print "%s : %s" % (k, ' '.join(map(str, sortSpans(ref2span[k]))))
    #print "---------------"

    for a in remove_list:
        try:
            new_annotations.remove(a)
        except ValueError:
            sys.stderr.write("Error: %s not in list! %s \n" % (a, DOCUMENT))

    return new_annotations

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
    parser.add_option("-l", "--list", dest="fileList",help="Filelist of featureDirs to process", type="string", action="store")
    parser.add_option("-o", "--out-file", dest="outfile",help="Name of file to write filelist of used docs to", type="string", action="store", default="")
    parser.add_option("-m", "--max-pairs", dest="M", help="Maximum number of pairs to produce", type="int", action="store", default=4000000)
    parser.add_option("-d", "--max-docs", dest="D", help="Maximum number of docs to use", type="int", action="store", default=-1)
    parser.add_option("-n", "--neg-pair-ratio", dest="N", help="Ratio of Neg/Pos pairs.", type="float", action="store", default=40.0)
    parser.add_option("-y", "--heuristic-pairs", dest="Y", help="# of heuristic pairs to include.", type="int", action="store", default=0)
    parser.add_option("-x", "--string-pairs", dest="X", help="# of string match pairs to include as a percentage of Y.", type="float", action="store", default=0.80)
    parser.add_option("-w", help="Write Reconcile output in directorys supplied by FILELIST", action="store_true", dest="write", default=False)
    parser.add_option("-q", help="Run quietly", action="store_true", dest="quiet", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if not options.quiet:
        print("======================")
        print("= The Great Leveling =")
        print("= Strings=> %0.2f     =" % (options.X))
        print("= Docs=> %d        =" % (options.D))
        print("= NegRatio=> %0.2f   =" % (options.N))
        print("= Total=> %d    =" % (options.M))
        print("======================")

    fileList = open(options.fileList, 'r')
    files = [x for x in fileList.readlines() if not x.startswith("#")]
    stringMatchPairs = defaultdict(list)
    heuristicPairs = defaultdict(list)
    finalPairs = defaultdict(list)

    if not options.quiet:
        print("Reading in %d files..." % (len(files)))
        prog = ProgressBar(len(files))
        sys.stdout.write("\r")
    totalDocs = 0
    for f in files:
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
        if len(all_pairs) > 0:
            totalDocs+=1
            if (options.D >= 0) and (totalDocs >= options.D):
                break
        if not options.quiet:
            prog.update_time(totalDocs)
            sys.stdout.write("\r%s" % (str(prog)))
            sys.stdout.flush()
    if not options.quiet:
        sys.stdout.write("\r \r\n")

    if options.D <= -1:
        options.D = totalDocs

    totalHeuristicPairs = 0
    for k in list(heuristicPairs.keys()):
        totalHeuristicPairs += len(heuristicPairs[k])

    totalStringMatches = 0
    for k in list(stringMatchPairs.keys()):
        totalStringMatches += len(stringMatchPairs[k])

    totalPairs = totalStringMatches+totalHeuristicPairs
    percentStringMatches = float(totalStringMatches)/totalPairs
    percentH = float(totalHeuristicPairs)/totalPairs

    if not options.quiet:
        print("======================")
        print("Total Heuristic Pairs: %d (%0.2f)%%" % (totalHeuristicPairs, percentH*100))
        print("Total String Matches: %d (%0.2f)%%" % (totalStringMatches, percentStringMatches*100))
        print("Total Pairs: %d" % (totalPairs))
        print("Total Docs: %d" % (totalDocs))
        print("Pair/Doc: %0.2f" % (float(totalPairs)/totalDocs))
        print("String Match Pair/Doc: %0.2f" % (float(totalStringMatches)/totalDocs))
        print("Heuristic Match Pair/Doc: %0.2f" % (float(totalHeuristicPairs)/totalDocs))
        print("======================")

    #add in all the heuristic pairs
    if not options.quiet:
        print("Adding Heuristic Pairs...", end=' ')
    for key in list(heuristicPairs.keys()):
        finalPairs[key] += heuristicPairs[key]
    if not options.quiet:
        print("Done.")

    if options.X == 1.0:
        use_all_strings=True
    else:
        use_all_strings = False

    if use_all_strings:
        for key in list(stringMatchPairs.keys()):
            finalPairs[key].extend(stringMatchPairs[key])
    else:
        #figure out how to divde the pairs
        str_matches_needed = ceil(options.X*totalStringMatches)
        if not options.quiet:
            print("Total String matches needed: %d" % (str_matches_needed))
            #print "Total Pairs needed: %d (%d string matches/%d other)" % (str_matches_needed+totalHeuristicPairs, str_matches_needed, totalHeuristicPairs)

            print("Generating sample...")
        sys.stdout.flush()
        sys.stdout.write("\r")
        prog = ProgressBar(int(str_matches_needed))

        found = 0
        while str_matches_needed > 0:
            doc = sample(list(stringMatchPairs.keys()),1)[0]
            pair = sample(stringMatchPairs[doc],1)[0]
            if doc not in list(finalPairs.keys()):
                finalPairs[doc].append(pair)
                str_matches_needed-=1
                if not options.quiet:
                    found +=1
                    prog.update_time(found)
                    sys.stdout.write("\r%s" % (str(prog)))
            else:
                if pair not in finalPairs[doc]:
                    finalPairs[doc].append(pair)
                    str_matches_needed-=1
                    if not options.quiet:
                        found+=1
                        prog.update_time(found)
                        sys.stdout.write("\r%s" % (str(prog)))
    if not options.quiet:
        sys.stdout.write("\r \r\n")
    total_final_pairs=0
    for key in list(finalPairs.keys()):
        total_final_pairs += len(finalPairs[key])

    outList = []
    real_total_pairs=0
    if options.write:
        if not options.quiet:
            print("Writing files...")
            sys.stdout.flush()
            sys.stdout.write("\r")
            prog = ProgressBar(len(list(finalPairs.keys())))
            found=0
        for f in list(finalPairs.keys()):
            DOCUMENT=f.strip()
            outList.append(int(f[f.rfind("/")+1:]))
            filename = f+"/annotations/level"
            collapsedPairs = collapse(finalPairs[f])
            collapsedChains = reconcile.chainAnnots(collapsedPairs)
            real_total_pairs += countPairs(collapsedChains)
            header = "this doc: %d pairs, %0.2f%% of total strings, 100%% of heuristic pairs, %d docs total" % (countPairs(collapsedChains), options.X, totalDocs)
            outputCollapsed(filename, collapsedPairs, header)
            #for c in collapsedChains:
            #    print c,len(c)
            #    if len(c) == 1:
            #        print c[0]
            #outputCollapsed(filename, collapse(finalPairs[f]), header)
            #output(filename,finalPairs[f],header)
            if not options.quiet:
                found +=1
                prog.update_time(found)
                sys.stdout.write("\r%s" % (str(prog)))
        if not options.quiet:
            sys.stdout.write("\r \r\n")
            print("Writing completed.")

    outList.sort()

    if options.outfile != "":
        reconcileFileList = open(options.outfile, 'w')
    else:
        reconcileFileList = open("rec.filelist", 'w')
    for i in outList:
        reconcileFileList.write("%s\n" % i)
    reconcileFileList.close()
    if not options.quiet:
        print("Total Pairs produced: %d" % real_total_pairs)
        print("Total Pairs (including negatives): %d" % (real_total_pairs*options.N))
        print("All Finished.")
        print("======================")
