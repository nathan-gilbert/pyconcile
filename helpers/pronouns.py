#!/usr/bin/python
# File Name : pronouns.py
# Purpose : 
# Creation Date : 11/15/2010
# Last Modified : Wed 02 Oct 2013 08:36:11 PM MDT
# Created By : Nathan Gilbert
#
# TODO: 1) change all heuristics to use annotations instead of just tuples.
#       2) tighten up the heuristics
#       3) add 2 more 
#       4) score.py now expects lists of annotations...
import sys
from optparse import OptionParser
from collections import defaultdict
from operator import itemgetter

from pyconcile import reconcile
from pyconcile import score
from pyconcile import data
from pyconcile import utils
from pyconcile import string_match
from pyconcile import pronoun_heuristics

def output(pairs, heurs):
    outFile = open("pronoun_pairs", 'w')
    i = 0
    for p in pairs:
        antecedent = p[0]
        anaphor = p[1]
        byte = (antecedent[0], antecedent[1], anaphor[0], anaphor[1])
        h = ','.join(map(lambda x : str(x), heurs[byte]))
        outFile.write("%d\t%d,%d\t%d,%d\tpronoun_pair_H=%s\t\n" % (i, antecedent[0], antecedent[1], anaphor[0], anaphor[1], h))
        i += 1
    outFile.close()

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dir", dest="directory",
            help="The base directory for this document", type="string",
            action="store")
    parser.add_option("-n", "--heuristics", dest="heuristics",
            help="The number of hueristics to use 0-8", type="int",
            action="store", default=-1)
    parser.add_option("-o", "--only", dest="only",
            help="A specific hueristic to run", type="int", action="store",
            default= -1)
    parser.add_option("-i", "--noit", help="Do not resolve it or its",
            action="store_true", dest="remove_its", default=False)
    parser.add_option("-1", "--no-1", help="Do not resolve first person",
            action="store_true", dest="remove_i", default=False)
    parser.add_option("-v", help="Verbose. Be it.", action="store_true",
            dest="verbose", default=False)
    parser.add_option("-V", "--vv", help="Very Verbose. Be Be it it.",
            action="store_true", dest="vverbose", default=False)
    parser.add_option("-a", help="Use all heuristics.", action="store_true",
            dest="all", default=False)
    parser.add_option("-s", help="Print small stats for this file.",
            action="store_true", dest="stats", default=False)
    parser.add_option("-c", help="Print pronoun counts for this file.",
            action="store_true", dest="counts", default=False)
    parser.add_option("-e", help="Evaluate the results (with annotated data.)",
            action="store_true", dest="evaluate", default=False)
    parser.add_option("-w", help="Write Reconcile output", action="store_true",
            dest="write", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    rawText = open(options.directory + "/raw.txt", 'r')
    allLines = ''.join(rawText.readlines())

    if options.stats:
        options.evaluate = False
        options.verbose = False
    print

    if options.all:
        options.heuristics = 8

    if options.vverbose:
        options.verbose = True

    nps = reconcile.getNPs_annots(options.directory)
    pronouns = reconcile.getPronouns(options.directory, "ALL")
    possessive_pronouns = reconcile.getPronouns(options.directory, "POSSESSIVE")
    sents = reconcile.getSentences(options.directory)
    nes = reconcile.getNEsByClass(options.directory, "PERSON")

    all_pairs = []
    counts = {}

    #remove dates
    nps = utils.remove_dates(nps)
    pronouns = utils.remove_dates(pronouns)
    possessive_pronouns = utils.remove_dates(possessive_pronouns)

    if options.remove_its:
        nps = utils.remove_hard_pronouns(nps)
        pronouns = utils.remove_hard_pronouns(pronouns)
        pronouns = utils.remove_hard_pronouns(pronouns)
        possessive_pronouns = utils.remove_hard_pronouns(possessive_pronouns)

    if options.remove_i:
        nps = utils.remove_i(nps)
        pronouns = utils.remove_i(pronouns)
        possessive_pronouns = utils.remove_i(possessive_pronouns)

    #heuristic 1
    if options.heuristics > 0 or (options.only == 1):
        if options.vverbose:
            print "Running Heuristic 1...",

        pairs1 = []
        for p in pronouns:
            counts[p.getATTR("text_lower")] = counts.get(p.getATTR("text_lower"), 0) + 1

            #get the nps from the prev sentence and the sentence in which the
            #pronoun is found.
            prev_nps = reconcile.sent2nps(reconcile.prev_sent(sents, p), nps) \
            + reconcile.sent2nps_prev(sents, nps, p)

            pairs1.extend(pronoun_heuristics.heuristic1(prev_nps, p))

        pairs1 = filter(lambda x : x != [], pairs1)
        if options.vverbose:
            print "%d resolutions" % len(pairs1)
        all_pairs.extend(pairs1)

    #heuristic 2
    if options.heuristics > 1 or (options.only == 2):
        if options.vverbose:
            print "Running Heuristic 2...",

        pairs2 = []
        for p in possessive_pronouns:
            counts[p.getATTR("text_lower")] = counts.get(p.getATTR("text_lower"), 0) + 1
            prev_nps = reconcile.sent2nps(reconcile.prev_sent(sents, p), nps) + reconcile.sent2nps_prev(sents, nps, p)
            pairs2.extend(pronoun_heuristics.heuristic2(prev_nps, p))

        pairs2 = filter(lambda x : x != [], pairs2)

        if options.vverbose:
            print "%d resolutions" % len(pairs2)
        all_pairs.extend(pairs2)

    #heuristic 3
    if options.heuristics > 2 or options.only == 3:
        if options.vverbose:
            print "Running Heuristic 3...",

        pairs3 = []
        for p in pronouns:
            counts[p.getATTR("text_lower")] = counts.get(p.getATTR("text_lower"), 0) + 1

            if (p.getATTR("text_lower") in data.FIRST_PER) \
                    and p.getATTR("in_quote"):
                pairs3.extend(pronoun_heuristics.heuristic3(allLines, nps, p))

        pairs3 = filter(lambda x : x != [], pairs3)
        if options.vverbose:
            print "%d resolutions" % len(pairs3)
        all_pairs.extend(pairs3)

    #heuristic 4
    if options.heuristics > 3 or options.only == 4:
        if options.vverbose:
            print "Running Heuristic 4...",

        pairs4 = pronoun_heuristics.heuristic4(nps, possessive_pronouns)
        pairs4 = filter(lambda x : x != [], pairs4)
        if options.vverbose:
            print "%d resolutions" % len(pairs4)

        all_pairs.extend(pairs4)

    #heuristic 5
    if options.heuristics > 4 or options.only == 5:
        if options.vverbose:
            print "Running Heuristic 5...",

        pairs5 = pronoun_heuristics.heuristic5(sents, pronouns)
        pairs5 = filter(lambda x : x != [], pairs5)

        if options.vverbose:
            print "%d resolutions" % len(pairs5)

        all_pairs.extend(pairs5)

    #heuristic 6 
    if options.heuristics > 5 or (options.only == 6):
        if options.vverbose:
            print "Running Heuristic 6...",
        pairs6 = []
        for p in pronouns:
            counts[p.getATTR("text_lower")] = counts.get(p.getATTR("text_lower"), 0) + 1
            prev_nps = reconcile.sent2nps(reconcile.prev_sent(sents, p), nps) + reconcile.sent2nps_prev(sents, nps, p)
            pairs6.extend(pronoun_heuristics.heuristic6(prev_nps, p))
        pairs6 = filter(lambda x : x != [], pairs6)
        if options.vverbose:
            print "%d resolutions" % len(pairs6)
        all_pairs.extend(pairs6)

    #heuristic 7
    if options.heuristics > 6 or (options.only == 7):
        if options.vverbose:
            print "Running Heuristic 7...",
        pairs7 = []
        for p in possessive_pronouns:
            counts[p.getATTR("text_lower")] = counts.get(p.getATTR("text_lower"), 0) + 1
            prev_nps = reconcile.sent2nps(reconcile.prev_sent(sents, p), nps) + reconcile.sent2nps_prev(sents, nps, p)
            pairs7.extend(pronoun_heuristics.heuristic7(prev_nps, p))
        pairs7 = filter(lambda x : x != [], pairs7)
        if options.vverbose:
            print "%d resolutions" % len(pairs7)
        all_pairs.extend(pairs7)

    #heuristic 8
    if options.heuristics > 7 or (options.only == 8):
        if options.vverbose:
            print "Running Heuristic 8...",
        pairs8 = []
        pairs8 = pronoun_heuristics.heuristic8(nps, pronouns)

        pairs8 = filter(lambda x : x != [], pairs8)
        if options.vverbose:
            print "%d resolutions" % len(pairs8)
        all_pairs.extend(pairs8)
    all_pairs = utils.flatten(all_pairs)

    tmp = []
    if options.verbose:
        #find duplicates in all_pairs
        heurs = defaultdict(list)
        for i in range(0, len(all_pairs)):
            curr = all_pairs[i]
            byte = (curr[0].getStart(), curr[0].getEnd(), curr[1].getStart(),
                    curr[1].getEnd())
            h = curr[2]
            if h not in heurs.get(byte, []):
                heurs[byte].append(h)

        if options.vverbose:
            print "==================="
            print "Resolutions:"
            print "==================="

        for p in all_pairs:
            if len(p) < 1:
                continue
            antecedent = p[0]
            anaphor = p[1]
            byte = (antecedent.getStart(), antecedent.getEnd(),
                    anaphor.getStart(), anaphor.getEnd())
            h = ','.join(map(lambda x : str(x), heurs[byte]))
            attrs1 = "sem=%s, gen=%s, num=%s" % (antecedent.getATTR("semantic"),
                    antecedent.getATTR("gender"),
                    antecedent.getATTR("number"))
            attrs2 = "sem=%s, gen=%s, num=%s" % (anaphor.getATTR("semantic"),
                    anaphor.getATTR("gender"),
                    anaphor.getATTR("number"))
            if byte not in tmp:
                tmp.append(byte)
                print "%s [%s] <- %s [%s] (H:%s)" % (antecedent.ppprint(), 
                        attrs1, anaphor.ppprint(), attrs2, h)

        if options.vverbose:
            print "==================="

    if options.evaluate:
        GoldChains = reconcile.getGoldChains(options.directory)
        s = score.accuracy(GoldChains, all_pairs)
        print "Document Score:"
        print "  Accuracy: %0.2f with %d Correct, %d Incorrect" % (s[0], s[1], s[2])

    if options.stats:
        GoldChains = reconcile.getGoldChains(options.directory)
        s = score.accuracy(GoldChains, all_pairs)
        print "%d %d %d" % (s[1], s[2], s[3])

    if options.write:
        heurs = defaultdict(list)
        UniquePairs = []
        for i in range(0, len(all_pairs)):
            curr = all_pairs[i]
            byte = (curr[0][0], curr[0][1], curr[1][0], curr[1][1])
            h = curr[2]

            #if this is the first time we are seeing this bytespan
            if heurs.get(byte, []) == []:
                UniquePairs.append(all_pairs[i])

            if h not in heurs.get(byte, []):
                heurs[byte].append(h)

        #output(all_pairs, heurs)
        output(UniquePairs, heurs)

    if options.counts:
        print "Total pronouns"
        for c in counts:
            print "%s : %d" % (c, counts[c])

