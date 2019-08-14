#!/usr/bin/python
'''
File Name : /uusoc/scratch/sollasollew/ngilbert/.workspace/pyconcile-tools/src/pyconcile-tools/existentials.py
Purpose : Find existential NPs and mark them.
Creation Date : May 23, 2011 3:43:53 PM
Last Modified : Wed 24 Aug 2011 05:32:15 PM MDT
@author: ngilbert
'''
import sys
from optparse import OptionParser

from pyconcile import reconcile
from pyconcile import score

def output(existentials, outfile):
    """output the set of existentials to file """
    num = 0
    outFile = open(outfile+"/existentials", 'w')
    for e in existentials:
        outFile.write("%d\t%d,%d\n" % (num, e.getStart(), e.getEnd()))
        num += 1
    outFile.close()

def gold_singletons(base_directory):
    nps = reconcile.getNPs_annots(base_directory)
    golds = reconcile.parseGoldAnnots(base_directory)
    existentials = []

    for n in nps:
        for g in golds:
            if n.contains(g) or g.contains(n):
                break
        else:
            if n not in existentials:
                existentials.append(n)
    return existentials

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l", help="Filelist", action="store",
            dest="filelist", default="")
    parser.add_option("-g", help="Use the gold heuristic", action="store_true",
            dest="use_gold", default=False)
    parser.add_option("-e", help="Evaluate yourself (on annotated data)",
            action="store_true", dest="evaluate", default=False)
    parser.add_option("-v", help="Verbose. Be it.", action="store_true",
            dest="verbose", default=False)
    parser.add_option("-w", help="Write Reconcile output", action="store_true",
            dest="write", default=False)
    parser.add_option("-s", help="Collect statistics on existentials",
            action="store_true", dest="stats", default=False)
    parser.add_option("-o", help="Outfile location", action="store",
            dest="outfile", type="string", default=".")
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    counts = {"proper" : 0, "common" : 0, "pronoun" : 0, "definite" : 0,
            "indefinite" : 0}

    fileList = open(options.filelist, 'r')

    total_existentials = []

    for directory in fileList:
        existentials = []
        directory = directory.strip()

        if options.use_gold:
            existentials = gold_singletons(directory)

        #update the counts
        if options.stats:
            for e in existentials:
                if e.getATTR("proper_name") != "false":
                    counts["proper"] = counts.get("proper", 0) + 1
                elif e.getATTR("pronoun") != "NONE":
                    counts["pronoun"] = counts.get("pronoun", 0) + 1
                else:
                    counts["common"] = counts.get("common", 0) + 1

        if options.verbose:
            for e in existentials:
                print("%s $!$ [sem=%s, num=%s, mod=%s, def=%s, ind=%s]" % \
                (e.pprint(),e.getATTR("semantic"), e.getATTR("number"),
                        e.getATTR("modifier"), e.getATTR("is_definite"),
                        e.getATTR("is_indefinite")))

        if options.evaluate:
            gold = gold_singletons(directory)
            s = score.singleton_accuracy(gold, existentials, True)
            print("Document Score:")
            print("  Accuracy: %0.2f with %d Correct, %d Incorrect and %d Markable Errors" % (s[0], s[1], s[2], s[3]))

        if options.write:
            output(existentials, options.outfile)

        total_existentials.extend(existentials)
    fileList.close()

    if options.verbose:
        #print out the counts:
        print("# of existentials: %d" % len(total_existentials))
        print("Counts: %d proper, %d pronoun, %d common" % (counts["proper"],
                counts["pronoun"], counts["common"]))
