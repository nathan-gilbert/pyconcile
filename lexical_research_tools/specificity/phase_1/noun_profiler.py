#!/usr/bin/python
# File Name : pronoun_profiler.py
# Purpose : Gather statistics on how pronouns are used in the wild.
# Creation Date : 05-01-2013
# Last Modified : Mon 13 May 2013 02:10:34 PM MDT
# Created By : Nathan Gilbert
#
import sys
import numpy
import nltk
from collections import defaultdict
#import matplotlib.pyplot as plt
from pylab import *

from pyconcile import reconcile
from pyconcile import data
from pyconcile import utils
from pyconcile.document import Document
from pyconcile.bar import ProgressBar
import specificity_utils

class Nominal:
    def __init__(self, t):
        self.text = t
        self.count = 1
        self.closest_antecedents = []
        self.word_distances = defaultdict(list)
        self.sent_distances = defaultdict(list)
        self.base_antecedent = 0
        self.singletons = 0
        self.pdtb = {"SAME_ARG" : 0, "DIFF_ARG" : 0, "NONE" : 0}
        self.unique = 0 # an anaphor we have not seen before.
        self.subj = 0
        self.dobj = 0

        #these three should sum up to the total antecedents
        self.string_matches = 0
        self.nominal_antecedent = 0
        self.proper_antecedent = 0

    def updateCount(self): self.count += 1
    def getCount(self): return self.count
    def getText(self): return self.text
    def addAntecedent(self, antecedent):
        if antecedent not in self.closest_antecedents:
            self.unique += 1
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
        for key in self.word_distances.keys():
            #key is a word
            for dist in self.word_distances[key]:
                histo[str(dist)] = histo.get(str(dist), 0) + 1
        return histo
    def sent_distance_histogram(self):
        histo = {}
        for key in self.sent_distances.keys():
            #key is a word
            for dist in self.sent_distances[key]:
                histo[str(dist)] = histo.get(str(dist), 0) + 1
        return histo

def add_stats(nominal_class, doc, anaphor, text):
    if text in nominal_class.keys():
        nominal_class[text].updateCount()
    else:
        nominal_class[text] = Nominal(text)

    #find the closest antecedent
    antecedent = doc.closest_antecedent(anaphor)
    if antecedent is not None:
        #print anaphor.ppprint(),
        #print antecedent.ppprint()

        #uniqueness -- what is the rate at which a pronoun is coreferent
        #with "new" words? I once called this generality -- captured with
        #antecedent
        nominal_class[text].addAntecedent(utils.textClean(antecedent.getText()).lower())

        #string matches -- how often does this pronoun resolve to
        #instances of itself?
        ant_text = utils.textClean(antecedent.getText()).lower()
        if ant_text == text:
            nominal_class[text].string_matches += 1

        #find the distance of the closest antecedent
        # 1. in word
        wd = doc.word_distance(antecedent, anaphor)
        nominal_class[text].word_distance(antecedent, wd)

        # 2. in sentences
        sd = doc.sentence_distance(antecedent, anaphor)
        nominal_class[text].sent_distance(antecedent, sd)

        ant_pdtb = doc.getContainedPDTB(antecedent)
        ana_pdtb = doc.getContainedPDTB(anaphor)

        # 3. pdtb parse distance ? what discourse parse values are useful?
        for pdtb1 in ant_pdtb:
            for pdtb2 in ana_pdtb:
                if pdtb1 == pdtb2:
                    #    a. if the anaphor and antecedent are in the same argument of a
                    #    discourse relation?
                    nominal_class[text].pdtb["SAME_ARG"] = nominal_class[text].pdtb["SAME_ARG"] + 1

                if (pdtb1.getATTR("TYPE") == pdtb2.getATTR("TYPE")) and (pdtb1.getATTR("SID") == pdtb2.getATTR("SID")):
                    #    b. if the anaphor and antecedent are in different arguments of the
                    #    same discourse relation
                    nominal_class[text].pdtb["DIFF_ARG"] = nominal_class[text].pdtb["DIFF_ARG"] + 1
        else:
        #    c. if the anaphor and antecedent are not in the same discourse
        #    relation at all
            nominal_class[text].pdtb["NONE"] = nominal_class[text].pdtb["NONE"] + 1

        #how often is this pronoun coreferent with a nominal?
        if specificity_utils.isNominal(antecedent):
            nominal_class[text].nominal_antecedent += 1

        #how often is this pronoun coreferent with a proper name?
        antecedent_np = doc.nps.getAnnotBySpan(antecedent.getStart(),
                antecedent.getEnd())
        if antecedent_np.getATTR("contains_pn") is not None:
            if antecedent_np.getATTR("contains_pn") == antecedent.getText():
                nominal_class[text].proper_antecedent += 1
        elif specificity_utils.isProper(antecedent_np):
            nominal_class[text].proper_antecedent += 1

        #how often are antecedents of this pronoun in the subj or dobj
        #position of a verb?
        if antecedent_np["GRAMMAR"] == "SUBJECT":
            nominal_class[text].subj += 1
        elif antecedent_np["GRAMMAR"] == "OBJECT":
            nominal_class[text].dobj += 1
    else:
        nominal_class[text].starts_chain()


def make_chart(histogram, dataset, chart_name, x_label, max_y=-1, max_x=-1):
    """
    """
    if max_x < 0:
        largest_x = -1
        l = max(map(lambda x : int(x), histogram.keys()))
        if l > largest_x:
            largest_x = l
    else:
        largest_x = max_x

    if max_y < 0:
        largest_y = -1
        l = max(histogram.values())
        if l > largest_y:
            largest_y = l
    else:
        largest_y = max_y

    # Create a new figure of size 8x8 points, using 150 dots per inch
    figure(figsize=(8,8), dpi=150)

    # Create a new subplot from a grid of 1x1
    plt = subplot(1,1,1)

    X = range(0, largest_x)
    T = [histogram.get(str(x), 0) for x in X]
    plot(X, T, color="blue", marker="o", linewidth=1.0, linestyle=":", label="proper nouns")

    ## Set x limits
    xlim(0, largest_x)
    # Set x ticks
    xticks(range(0, largest_x, 5))

    ## Set y limits
    ylim(0,largest_y)

    ## Set y ticks
    yticks(range(0, largest_y, 50))

    #legend(loc='upper right')
    plt.set_xlabel("{0}".format(x_label))
    plt.set_ylabel("Count")

    plt.set_title(dataset + " " + chart_name)

    legend(loc='upper right')

    ##Save figure using 72 dots per inch
    savefig("{0}_{1}.png".format(dataset,chart_name), dpi=150)

def make_pie_graph(dataset, stats):
    with open("piechart.stats", 'a') as outFile:
        for key in stats.keys():
            outFile.write("{0}$!${1}$!${2}\n".format(dataset, key, stats[key]))

def make_bar_chart(dataset,stats):
    with open("barchart.stats", 'a') as outFile:
        for key in stats.keys():
            outFile.write("{0}$!${1}$!${2}\n".format(dataset, key, stats[key]))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-list> <dataset> -plot" % (sys.argv[0])
        sys.exit(1)

    DATASET = sys.argv[2]

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    sys.stdout.flush()
    sys.stdout.write("\r")
    prog = ProgressBar(len(files))
    i = 0
    nominals = {}
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
            if (text in data.ALL_PRONOUNS):
                continue

            #if specificity_utils.isProper(np):
            #    continue
            anaphor_np = gold_nps.getAnnotBySpan(np.getStart(), np.getEnd())
            if anaphor_np["PROPER_NAME"] != "true" and anaphor_np["PROPER_NOUN"] != "true":
                continue

            #print text
            add_stats(nominals, doc, np, text)

        #true singletons -- TODO: double check that these numbers are correct
        for key in nominals.keys():
            nominals[key].singletons += doc.getSingletonCount(key)

    sys.stdout.write("\r \r\n")

    #histogram for sentence distance
    nominals_total_sent_histo = {}
    for key in nominals.keys():
        h = nominals[key].sent_distance_histogram()
        for dist in h.keys():
            nominals_total_sent_histo[dist] = nominals_total_sent_histo.get(dist, 0) + h[dist]

    #combine histograms
    make_chart(nominals_total_sent_histo, DATASET, "sentence_distance", "Sentence Distance",
            max_x=10)

    #histogram for word distance
    nominals_total_word_histo = {}
    for key in nominals.keys():
        h = nominals[key].wd_distance_histogram()
        for dist in h.keys():
            nominals_total_word_histo[dist] = nominals_total_word_histo.get(dist, 0) + h[dist]

    #combine histograms
    make_chart(nominals_total_word_histo, DATASET, "word_distance", "Word Distance", max_x=40)

    #The following charts would work better with the results across every
    #domain in one graph.
    #save these to a file, read them in another script to combine all
    #domains.
    #bar charts
    # 1. base antecedents
    stats = {}
    nominals_ba = 0
    for key in nominals.keys():
        nominals_ba += nominals[key].base_antecedent
    stats["T$!$BA"] = nominals_ba

    # 2. true singletons
    stats["T$!$SINGLE"] = 0
    for key in nominals.keys():
        stats["T$!$SINGLE"] = stats["T$!$SINGLE"] + nominals[key].singletons

    # 3. strings matches
    stats["T$!$STR"] = 0
    for key in nominals.keys():
        stats["T$!$STR"] = stats["T$!$STR"] + nominals[key].string_matches

    # 4. ratio of uniqueness
    stats["T$!$UNI"] = 0
    for key in nominals.keys():
        stats["T$!$UNI"] = stats["T$!$UNI"] + nominals[key].unique

    # 5. avg word distance +mean +std
    mean = numpy.mean(numpy.array(nominals_total_word_histo.values()))
    std_dev = numpy.std(numpy.array(nominals_total_word_histo.values()))
    stats["T$!$WORD_MEAN"] = mean
    stats["T$!$WORD_STD"] = std_dev

    #pie graphs? --right now they are bar graphs
    # 5. nominal/pronoun/proper pie graph
    stats["T$!$NOM"] = 0
    for key in nominals.keys():
        stats["T$!$NOM"] = stats["T$!$NOM"] + nominals[key].nominal_antecedent
    stats["T$!$PRO"] = 0
    for key in nominals.keys():
        stats["T$!$PRO"] = stats["T$!$PRO"] + nominals[key].string_matches
    stats["T$!$PRP"] = 0
    for key in nominals.keys():
        stats["T$!$PRP"] = stats["T$!$PRP"] + nominals[key].proper_antecedent

    # 6. same arg/diff arg/no arg pie graph
    stats["T$!$SAME_ARG"] = 0
    for key in nominals.keys():
        stats["T$!$SAME_ARG"] = stats["T$!$SAME_ARG"] + nominals[key].pdtb["SAME_ARG"]
    stats["T$!$DIFF_ARG"] = 0
    for key in nominals.keys():
        stats["T$!$DIFF_ARG"] = stats["T$!$DIFF_ARG"] + nominals[key].pdtb["DIFF_ARG"]

    # 7. subj/obj ratio of antecedents
    stats["T$!$SUBJ"] = 0
    for key in nominals.keys():
        stats["T$!$SUBJ"] = stats["T$!$SUBJ"] + nominals[key].subj
    stats["T$!$OBJ"] = 0
    for key in nominals.keys():
        stats["T$!$OBJ"] = stats["T$!$OBJ"] + nominals[key].dobj

    make_bar_chart(DATASET, stats)

    ## Show result on screen
    if "-plot" in sys.argv:
        show()
