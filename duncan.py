#!/usr/bin/python
# File Name : duncan.py
# Purpose : A set of methods for manipulating duncan produced annotations
# Creation Date : 12-02-2011
# Last Modified : Thu 14 Mar 2013 01:03:25 PM MDT
# Created By : Nathan Gilbert
#
import sys
import re
from collections import defaultdict

from . import reconcile
from . import utils
from .annotation import Annotation
from .annotation_set import AnnotationSet
from .union_find import UnionFind

def getDuncanAnnots(datadir):
    """Returns an annotation set of the original Duncan annotations. Only
    provides what was originally supplied in the annots"""

    SPAN = re.compile('(\d+),(\d+)')
    ID = re.compile('\s+ID=\"([^"]*)\"')
    REF = re.compile('REF=\"([^"]*)\"')
    H = re.compile('H=\"([^"]*)\"')

    annotations = AnnotationSet("duncan annots")
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()

    #NOTE reading in the duncan reprise annotations
    try:
        #inFile = open(datadir+"/annotations/duncan", 'r')
        inFile = open(datadir+"/annotations/duncan2", 'r')
    except:
        return annotations

    for line in inFile:
        line = line.strip()
        id_ref = None
        h = None

        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
            text_clean = utils.textClean(text)

        match = ID.search(line)
        if match:
            np_id = int(match.group(1))

        match = REF.search(line)
        if match:
            id_ref = match.group(1)

        match = H.search(line)
        if match:
            h = match.group(1)

        attr = {"TEXT":text, "REF": id_ref, "TEXT_CLEAN" : text_clean}
        if h is not None:
            attr["H"] = h

        a = Annotation(start, end, np_id, attr, text)
        annotations.add(a)
    return annotations

def getDuncanPairs(datadir):
    """ """
    duncan_annots = getDuncanAnnots(datadir)
    pairs = []
    for d in duncan_annots:
        if d.getATTR("REF") is not None:
            ant = duncan_annots.getAnnotByID(int(d.getATTR("REF")))
            pairs.append((ant, d))
    return pairs

def getDuncanPairsByH(datadir):
    duncan_annots = getDuncanAnnots(datadir)
    pairs = defaultdict(list)
    for d in duncan_annots:
        if d.getATTR("REF") is not None:
            ant = duncan_annots.getAnnotByID(int(d.getATTR("REF")))
            h = d.getATTR("H")
            pairs[h].append((ant, d))
    return pairs

def getBizarroDuncan(datadir):
    """Returns annotation pairs of bizzaro duncan annots """
    bizFile = open(datadir + "/annotations/bizarro")
    biz = []
    nps = reconcile.getNPs_annots(datadir)
    for line in bizFile:
        line = line.strip()
        tokens = line.split()

        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])

        start2 = int(tokens[2].split(",")[0])
        end2 = int(tokens[2].split(",")[1])

        ant = nps.getAnnotBySpan(start, end)
        ana = nps.getAnnotBySpan(start2, end2)

        if ant is not None and ana is not None:
            biz.append((ant, ana))
    return biz

def getDuncanChains(datadir):
    """Returns a dict with each value a duncan created coreference chain."""

    annots = getDuncanAnnots(datadir)

    uf = UnionFind()
    for a in annots:
        uf[a.getID()]

    for a in annots:
        if a.getATTR("REF") is not None:
            ref = int(a.getATTR("REF"))
            uf.union(ref, a.getID())

    chains = defaultdict(list)
    for c in uf:
        chains[uf[c]].append(annots.getAnnotByID(c))
        #print "%d : %d" % (c, uf[c])

    final_chains = defaultdict(list)
    for c in list(chains.keys()):
        final_chains[c] = reconcile.sortAnnotsBySpans(chains[c])
    return final_chains

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(("Usage: %s <dir>" % (sys.argv[0])))
        sys.exit(1)

    chains = getDuncanChains(sys.argv[1])
    for c in list(chains.keys()):
        print(("%d" % c))
        for mention in chains[c]:
            print(("  %s" % mention.ppprint()))
        print()

