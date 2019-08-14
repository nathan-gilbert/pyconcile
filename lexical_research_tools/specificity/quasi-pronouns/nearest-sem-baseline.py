#!/usr/bin/python
# File Name : nearest-sem-baseline.py
# Purpose : Match all qps with their closes (bytespan distance) antecedent.
# Creation Date : 12-10-2013
# Last Modified : Wed 22 Jan 2014 04:50:13 PM MST
# Created By : Nathan Gilbert
#
import sys
import os

from pyconcile import reconcile
from pyconcile import utils
from pyconcile.annotation_set import AnnotationSet

#TODO resolve regular pronouns too [save them separately from quasi pronouns]
#
def prevNPs(anaphor, nps):
    prev = []
    for np in nps:
        if np.getEnd() < anaphor.getStart():
            prev.append(np)
    return prev

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    PRONOUNS = ("he", "she", "it", "they", "them")
    USE_GOLD_NEs = False
    features_dir = "features.goldnps"
    predictions_dir = "predictions.Baseline.byte_dist"
    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        print("Working on {0}".format(f))

        nps = reconcile.getNPs(f)
        pronouns = AnnotationSet("pronouns")
        for np in nps:
            if np.getText().lower() in PRONOUNS:
                pronouns.add(np)

        #read in the faux pronouns
        quasi = reconcile.getFauxPronouns(f)
        if len(quasi) < 1 and len(pronouns) < 1:
            continue

        #resolve pronouns
        pronoun_resolutions = []
        for pro in pronouns:
            previous = prevNPs(pro, nps)
            antecedent = previous[-1]
            pronoun_resolutions.append((antecedent, pro))

        #these will need to be updated when we switch to non-ACE corpora
        if USE_GOLD_NEs:
            nes = reconcile.getGoldNEs(f)
        else:
            nes = reconcile.getNEs(f)

        resolutions = []
        for qp in quasi:
            previous = prevNPs(qp, nps)
            for np in reversed(previous):
                #TODO need to grab the non-gold NEs and use them as well.
                qp_ne = nes.getAnnotBySpan(qp.getStart(), qp.getEnd())
                np_ne = nes.getAnnotBySpan(np.getStart(), np.getEnd())

                #if semantics match, then resolve them.
                if qp_ne is not None and np_ne is not None:
                    if qp_ne["NE_CLASS"] == np_ne["NE_CLASS"]:
                        #print "{0:30} <= {1:30} : {2}".format(utils.textClean(np.getText()),
                        #        utils.textClean(qp.getText()), np_ne["NE_CLASS"]) 
                        resolutions.append((np, qp, np_ne["NE_CLASS"]))
                        break
                elif qp["SEMANTIC"] == np["SEMANTIC"]:
                    resolutions.append((np, qp, np["SEMANTIC"]))
                    break

        outdir = "{0}/{1}/{2}".format(f, features_dir, predictions_dir)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        #output in some format easy for counting the accuracy.
        with open(outdir+"/faux.predictions",'w') as outfile:
            outfile.write("#"+f+"\n")
            for res in resolutions:
                antecedent = res[0]
                anaphor    = res[1]
                sem        = res[2]
                outfile.write("{0},{1}\t{2},{3}\t{4} <- {5}\tSEM:{6}\n".format(
                    antecedent.getStart(), antecedent.getEnd(),
                    anaphor.getStart(), anaphor.getEnd(),
                    utils.textClean(antecedent.getText()),
                    utils.textClean(anaphor.getText()),
                    sem
                    ))

        #output in some format easy for counting the accuracy.
        with open(outdir+"/pronoun.predictions",'w') as outfile:
            outfile.write("#"+f+"\n")
            for res in pronoun_resolutions:
                antecedent = res[0]
                anaphor    = res[1]
                outfile.write("{0},{1}\t{2},{3}\t{4} <- {5}\n".format(
                    antecedent.getStart(), antecedent.getEnd(),
                    anaphor.getStart(), anaphor.getEnd(),
                    utils.textClean(antecedent.getText()),
                    utils.textClean(anaphor.getText())
                    ))

