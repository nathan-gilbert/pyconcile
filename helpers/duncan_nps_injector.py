#!/usr/bin/python
# File Name : duncan_nps_injector.py
# Purpose : Takes a list of NPs and looks at unannotated documents to ensure
# these NPs are included in a Reconcile nps files.
# Creation Date : 03-21-2013
# Last Modified : Thu 21 Mar 2013 10:53:41 AM MDT
# Created By : Nathan Gilbert
#
import sys
import re

from pyconcile import reconcile
from pyconcile.annotation import Annotation
from pyconcile import annotation_writer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <nps_list> <file_list>" % (sys.argv[0]))
        sys.exit(1)

    nps = []
    with open(sys.argv[1], 'r') as npsFile:
        for line in npsFile:
            if line.startswith("#"):
                continue
            line = line.strip()
            line = line.replace("Pair: ","")
            tokens = line.split(" <= ")

            if tokens[0] not in nps:
                nps.append(tokens[0].strip())
            if tokens[1] not in nps:
                nps.append(tokens[1].strip())

    files = []
    with open(sys.argv[2], 'r') as fileList:
        files.extend(fileList.readlines())

    total_nps_added = 0
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()

        origTxt = ""
        cleanTxt = ""
        with open(f+"/raw.txt", 'r') as rawTextFile:
            origTxt = ''.join(rawTextFile.readlines())
        cleanTxt = origTxt.replace("\n", " ").lower()

        #read in the Reconcile nps
        reconcile_nps = reconcile.getNPs(f)

        for np in nps:
            try:
                start_spans = [m.start() for m in re.finditer(" "+np+" ", cleanTxt)]
            except:
                continue
            for start in start_spans:
                start = start + 1
                end = start + len(np)
                if reconcile_nps.getAnnotBySpan(start, end) is not None:
                    continue
                else:
                    #create the annotation
                    new_np = Annotation(start, end, reconcile_nps.getNextID(),
                            {}, origTxt[start:end])
                    print("Adding new np: {0}".format(new_np.pprint()))
                    total_nps_added += 1
                    reconcile_nps.add(new_np)
        annotation_writer.write_annotations(f+"/annotations", reconcile_nps,
                "nps")

    print("Total new nps: {0}".format(total_nps_added))
    #for np in reconcile_nps:
    #    print np.pprint()


