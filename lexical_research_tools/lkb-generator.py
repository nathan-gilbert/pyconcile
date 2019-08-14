#!/usr/bin/python
# File Name : lkb-generator.py
# Purpose : Base script to generate the LKB of my dissertation
# Creation Date : 01-30-2013
# Last Modified : Tue 09 Apr 2013 02:44:45 PM MDT
# Created By : Nathan Gilbert
#
import sys
import time
import datetime
from collections import defaultdict
from optparse import OptionParser

from pyconcile import reconcile
from pyconcile import annotation
from pyconcile import utils
from entry import Entry

#globals
VERBOSE = False
DEBUG = False

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

    if (len(sys.argv) < 2) or (options.filelist == "") or (options.reconcile and options.lkb_outfile is None):
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        VERBOSE = True

    if options.debug:
        DEBUG = True

    start_time = time.time()
    files = []
    with open(options.filelist, 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    #start processing the annotated files
    doc_num = 1
    lkb = {}
    for f in files:
        doc_start_time = time.time()
        f = f.strip()
        print "Working on document: %s (%d/%d) " % (f, doc_num, len(files)),
        doc_num += 1
        gold_chains = reconcile.getGoldChains(f)
        gold_nps = reconcile.getNPs(f)
        reconcile.addSundanceProps(f, gold_nps)

        for gc in gold_chains.keys():
            for np1 in gold_chains[gc]:
                np1_text_ident = np1.getATTR("TEXT_CLEAN").lower()
                np1_text_ident = utils.cleanPre(np1_text_ident)

                #remove appositives too
                np1_text_ident = utils.remove_appositives(np1_text_ident)
                if np1_text_ident == "":
                    print >> sys.stderr, "NULL Ident Text: {0} Real Text: {1}".format(np1.getText(), f)
                    sys.exit(1)

                #creating the entry if necessary
                if np1_text_ident not in lkb.keys():
                    #create the entry
                    new_entry = Entry()
                    new_entry.setText(np1_text_ident)
                    new_entry.setDoc(f)

                    #deal with the "this semantic tag" <- the tag of this
                    #particular entity
                    tags = gold_nps.getAnnotBySpan(np1.getStart(), np1.getEnd()).getATTR("SUN_SEMANTIC")
                    if tags is not None:
                        for tag in tags:
                            new_entry.setSemanticTag("SU", tag)
                    lkb[np1_text_ident] = new_entry

                else:
                    lkb[np1_text_ident].updateCount(f)
                    tags = gold_nps.getAnnotBySpan(np1.getStart(), np1.getEnd()).getATTR("SUN_SEMANTIC")
                    if tags is not None:
                        for tag in tags:
                            lkb[np1_text_ident].setSemanticTag("SU", tag)

                for np2 in gold_chains[gc]:
                    if np1 == np2:
                        continue

                    np2_text_ident = np2.getATTR("TEXT_CLEAN")
                    #np2_text_ident = utils.cleanPre(np2_text_ident)
                    if np2_text_ident == "":
                        print >> sys.stderr, "NULL Ident Text: {0} Real Text: {1}".format(np2.getText(), f)
                        sys.exit(1)

                    #+get the word pair
                    lkb[np1_text_ident].addCoref(f, np2_text_ident)

                    #+get the sundance tag
                    tags = gold_nps.getAnnotBySpan(np2.getStart(),np2.getEnd()).getATTR("SUN_SEMANTIC")
                    np2_sundance_semantic_tags = tags if tags != "" else None
                    if np2_sundance_semantic_tags is not None:
                        for tag in np2_sundance_semantic_tags:
                            lkb[np1_text_ident].addSemantic("SU", np2_text_ident, tag)

                    #+get the first wordnet synset
                    np2_wn_semantic_tags = []
                    synsets = gold_nps.getAnnotBySpan(np2.getStart(),np2.getEnd()).getATTR("SYNSETS")

                    #only using the first synset for now.
                    if synsets != []:
                        np2_wn_semantic_tags = synsets[0]

                    for tag in np2_wn_semantic_tags:
                        lkb[np1_text_ident].addSemantic("WN", np2_text_ident, tag)

                    #+get the stanford label [only N possible things] 3 < N < 7
                    np2_stanford_semantic_tag = gold_nps.getAnnotBySpan(np2.getStart(),np2.getEnd()).getATTR("SEMANTIC")
                    if np2_stanford_semantic_tag != "UNKNOWN":
                        lkb[np1_text_ident].addSemantic("ST", np2_text_ident, np2_stanford_semantic_tag)

        doc_end_time = time.time()
        print "process time: %0.3f minutes" % ((doc_end_time-doc_start_time)/60)
    end_time = time.time()
    print "Total time: %0.3f minutes" % ((end_time-start_time)/60)
    sorted_entries = sorted(lkb.iteritems(), key=lambda x : x[1].getCount(),reverse=True)

    if options.reconcile:
        with open(options.lkb_outfile, 'w') as outfile:
            outfile.write("#Extracted from: {0} on {1}\n".format(options.filelist, datetime.datetime.now().strftime("%m-%d-%Y %H:%M %p")))
            for entry in sorted_entries:
                outfile.write(entry[1].reconcile_output())

    if options.human:
        for entry in sorted_entries:
            print entry[1]

