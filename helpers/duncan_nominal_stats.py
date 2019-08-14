#!/usr/bin/python
# File Name : duncan_nominal_stats.py
# Purpose : script to generate positive and negative instances from duncan
# (merged or not) files
# Creation Date : 12-02-2011
# Last Modified : Wed 28 Dec 2011 11:09:09 AM MST
# Created By : Nathan Gilbert
#
import sys
import cPickle as pickle
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import duncan
from pyconcile.nominal import Nominal

def makeNominal(ident, ft, doc, db):
    if ident not in db.keys():
        #make the nom
        nom = Nominal()
        nom.setText(ident)
        nom.addDoc(doc)
        nom.addFulltext(ft)
        db[ident] = nom
    else:
        db[ident].addDoc(doc)

#negative examples 
def getBizarroDuncanStats(datadir, t2n):
    """Adds in Bizarro Duncan negative examples. Bizarro Duncan creates
    negative instances based on NE class mismatch"""
    bizarro_pairs = duncan.getBizarroDuncan(datadir)
    pairs_added = 0

    for pair in bizarro_pairs:
        antecedent = pair[0]
        anaphor = pair[1]
        ana_text = anaphor.getATTR("TEXT_CLEAN").lower()

        #if ana_text in t2n.keys():
            #ante_text = antecedent.getATTR("TEXT_CLEAN").lower()
            #t2n[ana_text].updateDuncanAntiAntes(ante_text)
            #pairs_added += 1
            ##printing to std err
            #s = "%s <- %s\n" % (antecedent.getText(), anaphor.getText())
            #sys.stderr.write(s)
        #elif anaphor.getATTR("is_nominal"):
            #ante_text = antecedent.getATTR("TEXT_CLEAN").lower()

            ##this creates the nominal if hasn't been yet.
            #makeNominal(ana_text, anaphor.text, datadir, t2n)
            #t2n[ana_text].updateDuncanAntiAntes(ante_text)
            #t2n[ana_text].incrementCount()
            #pairs_added += 1

            #s = "%s <- %s\n" % (antecedent.getText(), anaphor.getText())
            #sys.stderr.write(s)
    return pairs_added

def getSundanceBizarroNegatives(t2n):
    """Adds in negative instances based on NE class information provided by
    Sundance"""
    pass

def getSundanceClauseNegatives(datadir, t2n):
    """Adds in the negatives produced by the Sundance clause heuristic """
    clauses = reconcile.getSundanceClauses(datadir)
    #duncan = 

def getFauxSoonNegatives(t2n):
    """Generate negative instance via the faux soon heuristic """
    pass

#positive examples
def getDuncanPositives(t2n):
    """Add in statistics regarding positive examples provided by Duncan"""
    pass

def add_in_duncan(duncan_files, t2n):
    """Generic method to add in what we choose to the current nominal set"""
    dFiles = open(duncan_files, 'r')
    for f in dFiles:
        f=f.strip()
        if f.startswith("#"):
            continue
        #print "Adding in Bizarro negatives from %s..." % f,
        #added = getBizarroDuncanStats(f, t2n)
        #print "%d added" % added
        getBizarroDuncanStats(f)

def getDuncanCorefStats(duncan_files, noun2antecedents):
    """Adds in the coreferent pairs from duncan"""

    dFiles = open(duncan_files, 'r')
    for f in dFiles:
        f=f.strip()
        if f.startswith("#"):
            continue

        print "Adding in Duncan positives from %s..." % f,
        added = 0
        #duncan_chains = duncan.getDuncanChains(f)
        #for key in duncan_chains.keys():
            #entity = duncan_chains[key]
            #for i in range(len(entity)-1, 1, -1):
                #anaphor = entity[i]
                #ana_text = anaphor.getATTR("TEXT_CLEAN").lower()
                #for j in range(i-1, 0, -1):
                    #antecedent = entity[j]
                    #ant_text = antecedent.getATTR("TEXT_CLEAN").lower()

                    #if ana_text == ant_text:
                        #continue

                    #noun2antecedents[ana_text][ant_text] = \
                    #noun2antecedents.get(ana_text, {}).get(ant_text, 0) + 1
                    #added += 1
        duncan_pairs = duncan.getDuncanPairs(f)
        for pair in duncan_pairs:
            antecedent = pair[0]
            anaphor = pair[1]
            ana_text = anaphor.getATTR("TEXT_CLEAN").lower()
            ant_text = antecedent.getATTR("TEXT_CLEAN").lower()

            if ana_text == ant_text:
                continue

            noun2antecedents[ana_text][ant_text] = \
            noun2antecedents.get(ana_text, {}).get(ant_text, 0) + 1
            added += 1

        print "%d positives found" % added
    dFiles.close()

def pickleDict(d, filename="stats.p"):
    pickle.dump(d, open(filename, "wb"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <first-argument>" % (sys.argv[0])
        sys.exit(1)

    noun2antecedents = defaultdict(dict)
    getDuncanCorefStats(sys.argv[1], noun2antecedents)
    pickleDict(noun2antecedents, "promed-duncan-stats.p")
