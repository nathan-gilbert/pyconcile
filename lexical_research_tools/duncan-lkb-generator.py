#!/usr/bin/python
# File Name : duncan-lkb-generator.py
# Purpose :
# Creation Date : 03-14-2013
# Last Modified : Wed 27 Mar 2013 03:03:28 PM MDT
# Created By : Nathan Gilbert
#
import sys
import re
import time
import datetime
from collections import defaultdict
from optparse import OptionParser

from entry import Entry
from pyconcile import utils
from pyconcile import duncan
from pyconcile import reconcile

#globals
VERBOSE = False
DEBUG = False
SPAN = re.compile('(\d+),(\d+)')
SEM = re.compile('.*SEM=\"([^"]*)\".*')

def addSundanceSemantics(np, snes):
    global SPAN, SEM
    for ne in snes:
        if (ne.getStart() >= np.getStart()) and (ne.getEnd() <= np.getEnd()):
            sem_start = ne.getStart() - np.getStart()
            if not utils.spanInPrep(sem_start, np.getText()) and not utils.spanInAppositive(sem_start,np.getText()):
                semantics = ne.getATTR("SUN_NE")
                if np.hasProp("SUN_SEMANTIC"):
                    for sem in semantics:
                        if sem not in np.attr["SUN_SEMANTIC"]:
                            np.attr["SUN_SEMANTIC"].append(sem)
                else:
                    np.setProp("SUN_SEMANTIC", semantics)

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filelist", help="List of files to process",
            action="store", dest="filelist", type="string", default="")
    parser.add_option("-v", "--verbose", help="Verbosity", action="store_true",
            dest="verbose", default=False)
    parser.add_option("-r", "--reconcile", help="Export knowledge base in Reconcile format",
            action="store_true", dest="reconcile", default=False)
    parser.add_option("-u", "--human", help="Export knowledge base in a human-friendly format",
            action="store_true", dest="human", default=False)
    parser.add_option("-o", "--out_file", help="The name of the exported file",
            action="store", type="string", default=None, dest="lkb_outfile")
    parser.add_option("-b", "--debug", help="Check diagnostics",
            action="store_true", dest="debug", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        sys.exit(1)

    start_time = time.time()
    files = []
    with open(options.filelist, 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    doc_num = 1
    lkb = {}
    for f in files:
        doc_start_time = time.time()
        f = f.strip()
        print "Working on document: %s (%d/%d) " % (f, doc_num, len(files)),
        doc_num += 1

        #read in duncan files
        duncan_pairs = duncan.getDuncanPairs(f)
        sundance_nes = reconcile.getSundanceNEs(f)

        for pair in duncan_pairs:
            antecedent = pair[0]
            addSundanceSemantics(antecedent, sundance_nes)
            anaphor = pair[1]
            addSundanceSemantics(anaphor, sundance_nes)

            ant_text_ident = utils.textClean(antecedent.getText().lower())
            ant_text_ident = utils.cleanPre(ant_text_ident)
            ant_text_ident = utils.remove_appositives(ant_text_ident)
            if ant_text_ident.endswith(","):
                ant_text_ident = ant_text_ident[:-1]
            if ant_text_ident == "":
                print >> sys.stderr, "NULL Ident Text: {0} Real Text: {1}".format(np1.getText(), f)
                sys.exit(1)

            #add duncan pairs to the lkb
            if ant_text_ident not in lkb.keys():
                #create the entry
                new_entry = Entry()
                new_entry.setText(ant_text_ident)
                new_entry.setDoc(f)

                tags = antecedent.getATTR("SUN_SEMANTIC")
                if tags is not None:
                    for tag in tags:
                        new_entry.setSemanticTag("SU", tag)
                lkb[ant_text_ident] = new_entry
            else:
                lkb[ant_text_ident].updateCount(f)
                tags = antecedent.getATTR("SUN_SEMANTIC")
                if tags is not None:
                    for tag in tags:
                        lkb[ant_text_ident].setSemanticTag("SU", tag)

            ana_text_ident = utils.textClean(anaphor.getText().lower())
            if ana_text_ident.endswith(","):
                ana_text_ident = ana_text_ident[:-1]
            if ana_text_ident == "":
                print >> sys.stderr, "NULL Ident Text: {0} Real Text: {1}".format(np2.getText(), f)
                sys.exit(1)

            #adding the coref pair
            lkb[ant_text_ident].addCoref(f, ana_text_ident)
            #might as well collect semantic information too!
            #+get the sundance tag
            tags = anaphor.getATTR("SUN_SEMANTIC")
            np2_sundance_semantic_tags = tags if tags != "" else None
            if np2_sundance_semantic_tags is not None:
                for tag in np2_sundance_semantic_tags:
                    lkb[ant_text_ident].addSemantic("SU", ana_text_ident, tag)
        doc_end_time = time.time()
        print "process time: %0.3f minutes" % ((doc_end_time-doc_start_time)/60)
    end_time = time.time()
    print "Total time: %0.3f minutes" % ((end_time-start_time)/60)
    sorted_entries = sorted(lkb.iteritems(), key=lambda x : x[1].getCount(),
            reverse=True)

    if options.reconcile:
        with open(options.lkb_outfile, 'w') as outfile:
            outfile.write("#Extracted from: {0} on {1}\n".format(options.filelist, datetime.datetime.now().strftime("%m-%d-%Y %H:%M %p")))
            for entry in sorted_entries:
                outfile.write(entry[1].reconcile_output())

    if options.human:
        for entry in sorted_entries:
            print entry[1]
