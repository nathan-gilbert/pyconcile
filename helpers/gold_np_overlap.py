#!/usr/bin/python
# File Name : gold_np_overlap.py
# Purpose : Prints out the response nps that overlap the gold NPs
# Creation Date : 11-22-2011
# Last Modified : Tue 22 Nov 2011 04:16:14 PM MST
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <dir>" % (sys.argv[0])
        sys.exit(1)

    #read in the response nps
    response_nps = reconcile.getNPs_annots(sys.argv[1])

    #read in the gsNPs file and find the matched
    gs_nps = reconcile.getGSNPs(sys.argv[1])

    for r_np in response_nps:
        for g_np in gs_nps:
            if g_np.getATTR("MATCHED") == r_np.getID():
                print "C :%s" % r_np.pprint()
                break
        else:
            print "I :%s" % r_np.pprint()
