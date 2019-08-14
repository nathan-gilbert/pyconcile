#!/usr/bin/python
# File Name : lkb-viewer.py
# Purpose : Methods for visualizing entries in the LKB.
# Creation Date : 01-30-2013
# Last Modified : Mon 22 Apr 2013 01:48:35 PM MDT
# Created By : Nathan Gilbert
#
import sys
import operator
from collections import defaultdict

import lkb_lib
from pyconcile import data

def print_entry(entry):
    final_string = "="*72
    final_string += "\n$: {0}".format(entry.getText())
    #final_string += "\nCount: {0}".format(entry.getCount())
    return final_string

def print_wordpairs(entry):
    CEs = entry.getAntecedentCounts()
    CEs = [x for x in list(CEs.keys()) if x not in data.ALL_PRONOUNS and x not in data.REL_PRONOUNS]
    CEs = [x for x in CEs if x != entry.getText()]
    final_CEs = []
    for ce in CEs:
        tokens = ce.split()
        if tokens[-1] != entry.getText():
            final_CEs.append(ce)

    CEs = final_CEs
    if len(CEs) < 1:
        return ""
    ce_string = ', '.join(CEs)
    return "CEs: {0}".format(ce_string)

def print_sundancepairs(entry):
    semantic_classes = entry.getNonStringMatchLSCounts("SU")
    total_semantic_classes = {}
    for cls in list(semantic_classes.keys()):
       total_semantic_classes[cls] = total_semantic_classes.get(cls, 0) + semantic_classes[cls]

    sorted_sem_classes = sorted(iter(total_semantic_classes.items()), key=operator.itemgetter(1), reverse=True)
    final_str = ""
    for pair in sorted_sem_classes:
        if pair[0] in ("UNKNOWN", "ENTITY"):
            continue
        final_str += "{0}:{1}, ".format(pair[0], pair[1])
    return "Sundance: {0}".format(final_str.strip()[:-1])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <lkb>" % (sys.argv[0]))
        sys.exit(1)

    lkb = lkb_lib.read_in_lkb(sys.argv[1])
    sorted_entries = sorted(iter(lkb.items()), key=lambda x : x[1].getCount(), reverse=True)
    for tup in sorted_entries:
        #we're skipping pronouns so far.
        if tup[0] in data.ALL_PRONOUNS or tup[0] in data.REL_PRONOUNS:
            continue

        entry = tup[1]
        if entry.getCount() >= 3:
            print_string = print_entry(entry)
            wp = print_wordpairs(entry)
            sp = print_sundancepairs(entry)
            if wp == "":
                #i.e. there are no none-string match or pronominal word pairs
                continue
            else:
                print(print_string)
                print(wp)
                #print sp

