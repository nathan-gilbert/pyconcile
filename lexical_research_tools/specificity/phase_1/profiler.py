#!/usr/bin/python
# File Name : profiler.py
# Purpose : Gather statistics on how different classes of nouns are used in the wild.
# Creation Date : 05-15-2013
# Last Modified : Mon 20 May 2013 12:21:58 PM MDT
# Created By : Nathan Gilbert
#
import sys
import numpy
import nltk
from collections import defaultdict
import matplotlib.pyplot as plt
from pylab import *

from pyconcile import reconcile
from pyconcile import data
from pyconcile import utils
from pyconcile.document import Document
from pyconcile.bar import ProgressBar
import specificity_utils

class Noun:
    def __init__(self, t):
        self.text = t
        self.count = 1
        self.closest_antecedents = []
        self.word_distances = defaultdict(list)
        self.sent_distances = defaultdict(list)
        self.base_antecedent = 0
        self.singletons = 0
        #self.pdtb = {"SAME_ARG" : 0, "DIFF_ARG" : 0, "NONE" : 0}
        self.productivity = 0 # an anaphor we have not seen before.
        self.subj_antecedent = 0
        self.dobj_antecedent = 0
        self.subj = 0
        self.dobj = 0

        #these three should sum up to the total antecedents
        self.string_matches = 0
        self.nominal_antecedent = 0
        self.proper_antecedent = 0
        self.pronoun_antecedent = 0

    def updateCount(self): self.count += 1
    def getCount(self): return self.count
    def getText(self): return self.text
    def addAntecedent(self, antecedent):
        if antecedent not in self.closest_antecedents:
            self.productivity += 1
        self.closest_antecedents.append(antecedent)
    def starts_chain(self):
        self.base_antecedent += 1
    def word_distance(self, ant, wd):
        ant_text = utils.textClean(ant.getText().lower()).strip()
        self.word_distances[ant_text].append(wd)
    def sent_distance(self, ant, sd):
        ant_text = utils.textClean(ant.getText().lower()).strip()
        self.sent_distances[ant_text].append(sd)
    def wd_distance_histogram(self):
        histo = {}
        for key in list(self.word_distances.keys()):
            #key is a word
            for dist in self.word_distances[key]:
                histo[str(dist)] = histo.get(str(dist), 0) + 1
        return histo

    def sent_distance_histogram(self):
        histo = {}
        for key in list(self.sent_distances.keys()):
            #the 'key' is an antecedent
            for dist in self.sent_distances[key]:
                #the 'dist' is the distance we have witnessed this antecedent
                #at
                histo[str(dist)] = histo.get(str(dist), 0) + 1
                #this histo is the distance -> number of antecedents at this
                #distance
        #this to distance -> # of antecedents within this
        #distance i.e. not normalized by counts yet
        #print histo
        return histo

        #below = 0
        #histo2 = {}
        #print range(0,  max(map(lambda x : int(x), histo.keys())))]
        #for i in range(0, max(map(lambda x : int(x), histo.keys()))+1):
        #    histo2[str(i)] = float(below + histo.get(str(i), 0))
        #    below += histo.get(str(i), 0)
        #print histo2
        #return histo2

def add_stats(noun_class, doc, anaphor, text):
    if text in list(noun_class.keys()):
        noun_class[text].updateCount()
    else:
        noun_class[text] = Noun(text)

    anaphor_np = doc.nps.getAnnotBySpan(anaphor.getStart(),
            anaphor.getEnd())
    if anaphor_np["GRAMMAR"] == "SUBJECT":
        noun_class[text].subj += 1
    elif anaphor_np["GRAMMAR"] == "OBJECT":
        noun_class[text].dobj += 1

    #find the closest antecedent
    antecedent = doc.closest_antecedent(anaphor)
    if antecedent is not None:
        #print anaphor.ppprint(),
        #print antecedent.ppprint()

        #productivity -- what is the rate at which a pronoun is coreferent
        #with "new" words? 
        noun_class[text].addAntecedent(utils.textClean(antecedent.getText()).lower())

        #string matches -- how often does this pronoun resolve to
        #instances of itself?
        ant_text = utils.textClean(antecedent.getText()).lower()
        if ant_text == text  \
            or (ant_text in ("he", "him") and text in ("he", "him")) \
            or (ant_text in ("they", "them") and text in ("they", "them")):
            noun_class[text].string_matches += 1

        #find the distance of the closest antecedent
        # 1. in word
        wd = doc.word_distance(antecedent, anaphor)
        noun_class[text].word_distance(antecedent, wd)

        # 2. in sentences
        sd = doc.sentence_distance(antecedent, anaphor)
        noun_class[text].sent_distance(antecedent, sd)

        #NOTE abandoning this for now
        #ant_pdtb = doc.getContainedPDTB(antecedent)
        #ana_pdtb = doc.getContainedPDTB(anaphor)
        # 3. pdtb parse distance ? what discourse parse values are useful?
        #for pdtb1 in ant_pdtb:
        #    for pdtb2 in ana_pdtb:
        #        if pdtb1 == pdtb2:
        #            #    a. if the anaphor and antecedent are in the same argument of a
        #            #    discourse relation?
        #            noun_class[text].pdtb["SAME_ARG"] = noun_class[text].pdtb["SAME_ARG"] + 1
        #
        #        if (pdtb1.getATTR("TYPE") == pdtb2.getATTR("TYPE")) and (pdtb1.getATTR("SID") == pdtb2.getATTR("SID")):
        #            #    b. if the anaphor and antecedent are in different arguments of the
        #            #    same discourse relation
        #            noun_class[text].pdtb["DIFF_ARG"] = noun_class[text].pdtb["DIFF_ARG"] + 1
        #else:
        ##    c. if the anaphor and antecedent are not in the same discourse
        ##    relation at all
        #    noun_class[text].pdtb["NONE"] = noun_class[text].pdtb["NONE"] + 1

        antecedent_np = doc.nps.getAnnotBySpan(antecedent.getStart(),
                antecedent.getEnd())

        if specificity_utils.isNominal(antecedent_np):
            #how often is this pronoun coreferent with a nominal?
            noun_class[text].nominal_antecedent += 1
        elif specificity_utils.isProper(antecedent_np):
            #how often is this pronoun coreferent with a proper name?
            noun_class[text].proper_antecedent += 1
        elif specificity_utils.isPronoun(antecedent_np):
            noun_class[text].pronoun_antecedent += 1
        else:
            #put dates here for now
            noun_class[text].nominal_antecedent += 1

        #how often are antecedents of this pronoun in the subj or dobj
        #position of a verb?
        if antecedent_np["GRAMMAR"] == "SUBJECT":
            noun_class[text].subj_antecedent += 1
        elif antecedent_np["GRAMMAR"] == "OBJECT":
            noun_class[text].dobj_antecedent += 1
    else:
        noun_class[text].starts_chain()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list> <dataset>" % (sys.argv[0]))
        sys.exit(1)

    DATASET = sys.argv[2]
    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    noun_classes = {
            "it"                      : {},
            "third_person"            : {},
            "third_person_plural"     : {},
            "it_possessive"           : {},
            "third_single_possessive" : {},
            "third_plural_possessive" : {},
            "nominal"                 : {},
            "proper"                  : {}
            }

    sys.stdout.flush()
    sys.stdout.write("\r")
    prog = ProgressBar(len(files))
    i = 0
    for f in files:
        if f.startswith("#"): continue
        f=f.strip()
        prog.update_time(i)
        sys.stdout.write("\r%s" % (str(prog)))
        sys.stdout.flush()
        i += 1

        doc = Document(f)
        #NOTE: still assuming that gold mentions are being supplied via
        #Reconcile.
        gold_nps = reconcile.getNPs(f)
        gold_chains = reconcile.getGoldChains(f)
        doc.addGoldChains(gold_chains)

        for np in gold_nps:
            text = utils.textClean(np.getText().lower()).strip()

            if text in data.THIRD_PERSON:
                #then it is he, him, she
                add_stats(noun_classes["third_person"], doc, np, text)
            elif (text in data.IT) and (text != "i"):
                #then we have 'it' or 'its'
                add_stats(noun_classes["it"], doc, np, text)
            elif text in data.THIRD_PERSON_PLURAL:
                #we have 'they' or 'them'
                add_stats(noun_classes["third_person_plural"], doc, np, text)
            elif text in data.THIRD_SINGULAR_POSSESSIVES:
                add_stats(noun_classes["third_single_possessive"], doc, np, text)
            elif text in data.THIRD_PLURAL_POSSESSIVES:
                add_stats(noun_classes["third_plural_possessive"], doc, np, text)
            elif text in data.IT_POSSESSIVE:
                add_stats(noun_classes["it_possessive"], doc, np, text)
            elif specificity_utils.isNominal(np):
                add_stats(noun_classes["nominal"], doc, np, text)
                #sys.stderr.write("{0}\n".format(text))
            elif specificity_utils.isProper(np):
                add_stats(noun_classes["proper"], doc, np, text)
                #sys.stderr.write("{0}\n".format(text))
            else:
                #sys.stderr.write("Word not found: {0}\n".format(text))
                continue

        #true singletons -- TODO double check that these numbers are correct
        #this word exists outside of annotations
        #This needs to take place at the document level and cycle over all the
        for cls in list(noun_classes.keys()):
            for word in noun_classes[cls]:
                noun_classes[cls][word].singletons += doc.getSingletonCount(word)

    sys.stdout.write("\r \r\n")

    #TODO printount the stats
    #with open("nouns.stats", "a") as outFile:
    for cls in sorted(noun_classes.keys()):
        total_antecendents = 0
        total_productivity = 0
        total_nominal_antecedents = 0
        total_proper_antecedents = 0
        total_pronoun_antecedents = 0
        total_subject_antecedents = 0
        total_object_antecedents = 0
        total_self_subject = 0
        total_self_object = 0
        total_string_match = 0
        total_counts = 0
        total_starts_chain = 0
        sent_dist = {}

        for word in noun_classes[cls]:
            total_antecendents += len(noun_classes[cls][word].closest_antecedents)
            total_productivity += noun_classes[cls][word].productivity
            total_nominal_antecedents += noun_classes[cls][word].nominal_antecedent
            total_proper_antecedents += noun_classes[cls][word].proper_antecedent
            total_pronoun_antecedents += noun_classes[cls][word].pronoun_antecedent
            total_subject_antecedents += noun_classes[cls][word].subj_antecedent
            total_object_antecedents += noun_classes[cls][word].dobj_antecedent
            total_string_match += noun_classes[cls][word].string_matches
            total_self_subject += noun_classes[cls][word].subj
            total_self_object += noun_classes[cls][word].dobj
            total_counts += noun_classes[cls][word].count
            total_starts_chain += noun_classes[cls][word].base_antecedent

            word_dist = noun_classes[cls][word].sent_distance_histogram()
            for d in list(word_dist.keys()):
                sent_dist[d] = sent_dist.get(d, 0) + word_dist[d]

        print("-"*72)
        print("Class: {0}".format(cls))
        print("Words                        : {0}".format(len(noun_classes[cls])))
        print("Total Antecedents            : {0}".format(total_antecendents))
        print("Productivity of Class        : {0:2.2f}".format(float(total_productivity)/total_antecendents))
        print("Inverse Productivity of Class: {0:2.2f}".format(float(total_antecendents)/total_productivity))
        print("Starts Chain                 : {0:2.2f}".format(float(total_starts_chain)/total_counts))
        print("."*72)
        print("Nominal %: {0:.2%}".format(float(total_nominal_antecedents) / total_antecendents))
        print("Proper  %: {0:.2%}".format(float(total_proper_antecedents) / total_antecendents))
        print("Pronoun %: {0:.2%}".format(float(total_pronoun_antecedents) / total_antecendents))
        print("."*72)
        print("Antecedent is Subject %: {0:4.2f}".format(float(total_subject_antecedents) / total_antecendents))
        print("Antecedent is Object  %: {0:4.2f}".format(float(total_object_antecedents) / total_antecendents))
        print("Self is Subject       %: {0:4.2f}".format(float(total_self_subject) / total_counts))
        print("Self is Object        %: {0:4.2f}".format(float(total_self_object) / total_counts))
        print("."*72)
        print("String matches %: {0:.2%}".format(float(total_string_match) / total_antecendents))
        print("."*72)
        zero_sentence = sent_dist.get("0", 0)
        print("Antecedents within 0 sent: {0:5.2f}".format(float(zero_sentence) / total_antecendents))
        one_sentence = zero_sentence + sent_dist.get("1", 0)
        print("Antecedents within 1 sent: {0:5.2f}".format(float(one_sentence) / total_antecendents))
        two_sentence = one_sentence + sent_dist.get("2", 0)
        print("Antecedents within 2 sent: {0:5.2f}".format(float(two_sentence) / total_antecendents))
        three_sentence = two_sentence + sent_dist.get("3", 0)
        print("Antecedents within 3 sent: {0:5.2f}".format(float(three_sentence) / total_antecendents))
        four_sentence = three_sentence + sent_dist.get("4", 0)
        print("Antecedents within 4 sent: {0:5.2f}".format(float(four_sentence) / total_antecendents))
        five_sentence = four_sentence + sent_dist.get("5", 0)
        print("Antecedents within 5 sent: {0:5.2f}".format(float(five_sentence) / total_antecendents))
        print("-"*72)
        print()
