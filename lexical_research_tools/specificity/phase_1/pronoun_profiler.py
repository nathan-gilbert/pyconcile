#!/usr/bin/python
# File Name : pronoun_profiler.py
# Purpose : Gather statistics on how pronouns are used in the wild.
# Creation Date : 05-01-2013
# Last Modified : Mon 13 May 2013 01:45:22 PM MDT
# Created By : Nathan Gilbert
#
import sys
import numpy
import nltk
from collections import defaultdict
#import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from pylab import *

from pyconcile import reconcile
from pyconcile import data
from pyconcile import utils
from pyconcile.document import Document
from pyconcile.bar import ProgressBar
import specificity_utils

class Pronoun:
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
        #return histo

        below = 0
        histo2 = {}
        #print range(0,  max(map(lambda x : int(x), histo.keys())))]
        for i in range(0, max(map(lambda x : int(x), histo.keys()))+1):
            histo2[str(i)] = float(below + histo.get(str(i), 0))
            below += histo.get(str(i), 0)
        #print histo2
        return histo2

def add_stats(pronoun_class, doc, anaphor, text):
    if text in pronoun_class.keys():
        pronoun_class[text].updateCount()
    else:
        pronoun_class[text] = Pronoun(text)

    #find the closest antecedent
    antecedent = doc.closest_antecedent(anaphor)
    if antecedent is not None:
        #print anaphor.ppprint(),
        #print antecedent.ppprint()

        #uniqueness -- what is the rate at which a pronoun is coreferent
        #with "new" words? I once called this generality -- captured with
        #antecedent
        pronoun_class[text].addAntecedent(utils.textClean(antecedent.getText()).lower())

        #string matches -- how often does this pronoun resolve to
        #instances of itself?
        ant_text = utils.textClean(antecedent.getText()).lower()
        if ant_text == text  \
            or (ant_text in ("he", "him") and text in ("he", "him")) \
            or (ant_text in ("they", "them") and text in ("they", "them")):
            pronoun_class[text].string_matches += 1

        #find the distance of the closest antecedent
        # 1. in word
        wd = doc.word_distance(antecedent, anaphor)
        pronoun_class[text].word_distance(antecedent, wd)

        # 2. in sentences
        sd = doc.sentence_distance(antecedent, anaphor)
        pronoun_class[text].sent_distance(antecedent, sd)

        #ant_pdtb = doc.getContainedPDTB(antecedent)
        #ana_pdtb = doc.getContainedPDTB(anaphor)
        # 3. pdtb parse distance ? what discourse parse values are useful?
        #for pdtb1 in ant_pdtb:
        #    for pdtb2 in ana_pdtb:
        #        if pdtb1 == pdtb2:
        #            #    a. if the anaphor and antecedent are in the same argument of a
        #            #    discourse relation?
        #            pronoun_class[text].pdtb["SAME_ARG"] = pronoun_class[text].pdtb["SAME_ARG"] + 1
        #
        #        if (pdtb1.getATTR("TYPE") == pdtb2.getATTR("TYPE")) and (pdtb1.getATTR("SID") == pdtb2.getATTR("SID")):
        #            #    b. if the anaphor and antecedent are in different arguments of the
        #            #    same discourse relation
        #            pronoun_class[text].pdtb["DIFF_ARG"] = pronoun_class[text].pdtb["DIFF_ARG"] + 1
        #else:
        ##    c. if the anaphor and antecedent are not in the same discourse
        ##    relation at all
        #    pronoun_class[text].pdtb["NONE"] = pronoun_class[text].pdtb["NONE"] + 1

        #how often is this pronoun coreferent with a nominal?
        if specificity_utils.isNominal(antecedent):
            pronoun_class[text].nominal_antecedent += 1

        #how often is this pronoun coreferent with a proper name?
        antecedent_np = doc.nps.getAnnotBySpan(antecedent.getStart(),
                antecedent.getEnd())
        if antecedent_np.getATTR("contains_pn") is not None:
            if antecedent_np.getATTR("contains_pn") == antecedent.getText():
                pronoun_class[text].proper_antecedent += 1
        elif specificity_utils.isProper(antecedent_np):
            pronoun_class[text].proper_antecedent += 1

        #how often are antecedents of this pronoun in the subj or dobj
        #position of a verb?
        if antecedent_np["GRAMMAR"] == "SUBJECT":
            pronoun_class[text].subj += 1
        elif antecedent_np["GRAMMAR"] == "OBJECT":
            pronoun_class[text].dobj += 1
    else:
        pronoun_class[text].starts_chain()


def make_chart(histograms, dataset, chart_name, x_label, max_y=-1, max_x=-1):
    """
    """
    if max_x < 0:
        largest_x = -1
        for h in histograms:
            l = max(map(lambda x : int(x), h.keys()))
            if l > largest_x:
                largest_x = l
    else:
        largest_x = max_x

    if max_y < 0:
        largest_y = -1
        for h in histograms:
            l = max(h.values())
            if l > largest_y:
                largest_y = l
    else:
        largest_y = max_y

    # Create a new figure of size 8x8 points, using 150 dots per inch
    figure(figsize=(8,8), dpi=150)

    # Create a new subplot from a grid of 1x1
    plt = subplot(1,1,1)

    X = range(0, largest_x)
    T = [histograms[0].get(str(x), 0) for x in X]
    plot(X, T, color="blue", marker="o", linewidth=1.0, linestyle=":", label="third person singular")
    I = [histograms[1].get(str(x), 0) for x in X ]
    plot(X, I, color="red", marker="s", linewidth=1.0, linestyle=":", label="it")
    TP = [histograms[2].get(str(x), 0) for x in X]
    plot(X, TP, color="green", marker="D", linewidth=1.0, linestyle=":", label="third person plural")

    ## Set x limits
    xlim(0, largest_x)
    # Set x ticks
    xticks(range(0, largest_x, 5))

    ## Set y limits
    ylim(0,int(largest_y))

    ## Set y ticks
    yticks(range(0, int(largest_y), 5))

    #legend(loc='upper right')
    plt.set_xlabel("{0}".format(x_label))
    plt.set_ylabel("% of total antecedents")

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

    third_person = {}
    it = {}
    third_person_plural = {}

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
                add_stats(third_person, doc, np, text)
            elif (text in data.IT) and (text != "i"):
                #then we have 'it' or 'its'
                add_stats(it, doc, np, text)
            elif text in data.THIRD_PERSON_PLURAL:
                #we have 'they' or 'them'
                add_stats(third_person_plural, doc, np, text)
            else: continue

        #true singletons -- TODO: double check that these numbers are correct
        for key in it.keys():
            it[key].singletons += doc.getSingletonCount(key)
        for key in third_person.keys():
            third_person[key].singletons += doc.getSingletonCount(key)
        for key in third_person_plural.keys():
            third_person_plural[key].singletons += doc.getSingletonCount(key)

        #this word exists outside of annotations
        #This needs to take place at the document level and cycle over all the
        #pronouns we want to check

    sys.stdout.write("\r \r\n")
    #print "{0:5} : {1}".format("it", it["it"].getCount())
    #print it["it"].wd_distance_histogram()
    #print it["it"].sent_distance_histogram()
    #print "{0} : total antecedents".format(sum(it["it"].sent_distance_histogram().values()))
    #print "{0} : total antecedents".format(sum(it["it"].wd_distance_histogram().values()))
    #print "{0} : base antecedent instances".format(it["it"].base_antecedent)
    #for key in third_person.keys():
        #print "{0:5} : {1}".format(key, third_person[key].getCount())
        #print "{0} : total antecedents".format(sum(third_person[key].wd_distance_histogram().values()))
        #print "{0} : base antecedent instances".format(third_person[key].base_antecedent)
        #print third_person[key].sent_distance_histogram()
    #for key in third_person_plural.keys():
        #print "{0:5} : {1}".format(key, third_person_plural[key].getCount())
        #print third_person_plural[key].sent_distance_histogram()
        #print "{0} : total antecedents".format(sum(third_person_plural[key].wd_distance_histogram().values()))
        #print "{0} : base antecedent instances".format(third_person_plural[key].base_antecedent)

    #histogram for sentence distance
    third_person_total_sent_histo = {}
    t_total_antecedents = 0
    for key in third_person.keys():
        h = third_person[key].sent_distance_histogram()
        t_total_antecedents += len(third_person[key].closest_antecedents)
        for dist in sorted(h.keys(), key=lambda x: int(x)):
            #print key, dist, h[dist]
            #NOTE needs to bookkeep better when switching pronouns
            third_person_total_sent_histo[dist] = third_person_total_sent_histo.get(dist, 0) + h[dist]

    #print third_person_total_sent_histo
    keys = third_person_total_sent_histo.keys()
    keys = sorted(keys, key=lambda x : int(x))
    for key in keys:
        print "{0} : {1} / {2} = {3}".format(key, third_person_total_sent_histo[key],
                t_total_antecedents,
                float(third_person_total_sent_histo[key])/t_total_antecedents)
    print

    it_total_sent_histo = {}
    it_total_antecedents = 0
    for key in it.keys():
        h = it[key].sent_distance_histogram()
        it_total_antecedents += len(it[key].closest_antecedents)
        for dist in h.keys():
            it_total_sent_histo[dist] = it_total_sent_histo.get(dist, 0) + h[dist]

    keys = it_total_sent_histo.keys()
    keys = sorted(keys, key=lambda x : int(x))
    for key in keys:
        print "{0} : {1} / {2} = {3}".format(key, it_total_sent_histo[key],
                it_total_antecedents,
                float(it_total_sent_histo[key]/it_total_antecedents))

    third_person_plural_total_sent_histo = {}
    tp_total_antecedents = 0
    for key in third_person_plural.keys():
        h = third_person_plural[key].sent_distance_histogram()
        tp_total_antecedents += len(third_person_plural[key].closest_antecedents)
        for dist in h.keys():
            third_person_plural_total_sent_histo[dist] = third_person_plural_total_sent_histo.get(dist, 0) + h[dist]

    print
    #print third_person_plural_total_sent_histo
    keys = third_person_plural_total_sent_histo.keys()
    keys = sorted(keys, key=lambda x : int(x))
    for key in keys:
        print "{0} {1} / {2} = {3}".format(key, third_person_plural_total_sent_histo[key],
                tp_total_antecedents,
                float(third_person_plural_total_sent_histo[key]/tp_total_antecedents))

    #combine histograms
    #histograms = (third_person_total_sent_histo,
    #        it_total_sent_histo,
    #        third_person_plural_total_sent_histo)
    #make_chart(histograms, DATASET, "sentence_distance", "Sentence Distance",
    #        max_x=10)

    #make bar charts
    #word_classes = ("I", "TP", "T")
    #word_classes = ("I")
    #N = len(word_classes)
    #ind = numpy.arange(N) # the x locations for the groups
    #width = 0.10       # the width of the bars
    #colors = ('r','b','g','y','p')

    #fig = plt.figure(figsize=(8,8),dpi=150)
    #ax = fig.add_subplot(111)
    #rects = []
    #i=0
    #gap=0
    #for w_cls in word_classes:
        #percentages = []
        #for j in range(0, max_dist):
            #if w_cls == "I":
                #p = float(it_total_sent_histo.get(str(j), 0)) / it_total_antecedents
                #percentages.append(p*100)
            #elif w_cls == "TP":
                #p = float(tp_total_sent_histo.get(str(j), 0)) / tp_total_antecedents
                #percentages.append(p*100)
            #elif  w_cls == "T":
                #p = float(t_total_sent_histo.get(str(j), 0)) / t_total_antecedents
                #percentages.append(p*100)

        #print percentages
        #rect = ax.bar(ind+gap, percentages, width, color=colors[i])
        #rects.append(rect[0])
        #i+=1
        #gap+=width

    ### add some
    #ax.set_ylim(0, 100)
    #ax.set_yticks(range(0, 100, 10))
    #ax.set_ylabel('% of antecedents')
    #ax.set_xticks(ind+width)
    #ax.set_xticklabels(word_classes)
    #ax.set_title('Sentence distance')

    ##rects = rects[:len(datasets)]
    ##if len(rects) < 1: continue
    #ax.legend(rects, datasets, loc="upper right")

    ##savefig("{0}.png".format(dataset+"_sentence_distance"), dpi=150)
        ##autolabel(rects1)
        ##autolabel(rects2)
    #plt.show()

    ##histogram for word distance
    ##third_person_total_word_histo = {}
    ##for key in third_person.keys():
    ##    h = third_person[key].wd_distance_histogram()
    ##    for dist in h.keys():
    ##        third_person_total_word_histo[dist] = third_person_total_word_histo.get(dist, 0) + h[dist]

    ##it_total_word_histo = {}
    ##for key in it.keys():
    ##    h = it[key].wd_distance_histogram()
    ##    for dist in h.keys():
    ##        it_total_word_histo[dist] = it_total_word_histo.get(dist, 0) + h[dist]

    ##third_person_plural_total_word_histo = {}
    ##for key in third_person_plural.keys():
    ##    h = third_person_plural[key].wd_distance_histogram()
    #    for dist in h.keys():
    #        third_person_plural_total_word_histo[dist] = third_person_plural_total_word_histo.get(dist, 0) + h[dist]

    #combine histograms
    #histograms = (third_person_total_word_histo,
    #        it_total_word_histo,
    #        third_person_plural_total_word_histo)
    #make_chart(histograms, DATASET, "word_distance", "Word Distance", max_x=40)

    #The following charts would work better with the results across every
    #domain in one graph.
    #save these to a file, read them in another script to combine all
    #domains.
    #bar charts
    # 1. base antecedents
    #stats = {}
    #third_person_ba = 0
    #for key in third_person.keys():
        #third_person_ba += third_person[key].base_antecedent
    #stats["T$!$BA"] = third_person_ba

    #it_ba = 0
    #for key in it.keys():
        #it_ba += it[key].base_antecedent
    #stats["IT$!$BA"] = it_ba

    #third_person_plural_ba = 0
    #for key in third_person_plural.keys():
        #third_person_plural_ba += third_person_plural[key].base_antecedent
    #stats["TP$!$BA"] = third_person_ba

    ## 2. true singletons
    #stats["T$!$SINGLE"] = 0
    #for key in third_person.keys():
        #stats["T$!$SINGLE"] = stats["T$!$SINGLE"] + third_person[key].singletons
    #stats["IT$!$SINGLE"] = 0
    #for key in it.keys():
        #stats["IT$!$SINGLE"] = stats["IT$!$SINGLE"] + it[key].singletons
    #stats["TP$!$SINGLE"] = 0
    #for key in third_person_plural.keys():
        #stats["TP$!$SINGLE"] = stats["TP$!$SINGLE"] + third_person_plural[key].singletons

    ## 3. strings matches
    #stats["T$!$STR"] = 0
    #for key in third_person.keys():
        #stats["T$!$STR"] = stats["T$!$STR"] + third_person[key].string_matches
    #stats["IT$!$STR"] = 0
    #for key in it.keys():
        #stats["IT$!$STR"] = stats["IT$!$STR"] + it[key].string_matches
    #stats["TP$!$STR"] = 0
    #for key in third_person_plural.keys():
        #stats["TP$!$STR"] = stats["TP$!$STR"] + third_person_plural[key].string_matches

    ## 4. ratio of uniqueness
    #stats["T$!$UNI"] = 0
    #for key in third_person.keys():
        #stats["T$!$UNI"] = stats["T$!$UNI"] + third_person[key].unique
    #stats["IT$!$UNI"] = 0
    #for key in it.keys():
        #stats["IT$!$UNI"] = stats["IT$!$UNI"] + it[key].unique
    #stats["TP$!$UNI"] = 0
    #for key in third_person_plural.keys():
        #stats["TP$!$UNI"] = stats["TP$!$UNI"] + third_person_plural[key].unique

    ## 5. avg word distance +mean +std
    #mean = numpy.mean(numpy.array(third_person_total_word_histo.values()))
    #std_dev = numpy.std(numpy.array(third_person_total_word_histo.values()))
    #stats["T$!$WORD_MEAN"] = mean
    #stats["T$!$WORD_STD"] = std_dev

    #mean = numpy.mean(numpy.array(it_total_word_histo.values()))
    #std_dev = numpy.std(numpy.array(it_total_word_histo.values()))
    #stats["IT$!$WORD_MEAN"] = mean
    #stats["IT$!$WORD_STD"] = std_dev

    #mean = numpy.mean(numpy.array(third_person_plural_total_word_histo.values()))
    #std_dev = numpy.std(numpy.array(third_person_plural_total_word_histo.values()))
    #stats["TP$!$WORD_MEAN"] = mean
    #stats["TP$!$WORD_STD"] = std_dev

    ##pie graphs? --right now they are bar graphs

    ## 5. nominal/pronoun/proper pie graph
    #stats["T$!$NOM"] = 0
    #for key in third_person.keys():
        #stats["T$!$NOM"] = stats["T$!$NOM"] + third_person[key].nominal_antecedent
    #stats["T$!$PRO"] = 0
    #for key in third_person.keys():
        #stats["T$!$PRO"] = stats["T$!$PRO"] + third_person[key].string_matches
    #stats["T$!$PRP"] = 0
    #for key in third_person.keys():
        #stats["T$!$PRP"] = stats["T$!$PRP"] + third_person[key].proper_antecedent

    #stats["IT$!$NOM"] = 0
    #for key in it.keys():
        #stats["IT$!$NOM"] = stats["IT$!$NOM"] + it[key].nominal_antecedent
    #stats["IT$!$PRO"] = 0
    #for key in it.keys():
        #stats["IT$!$PRO"] = stats["IT$!$PRO"] + it[key].string_matches
    #stats["IT$!$PRP"] = 0
    #for key in it.keys():
        #stats["IT$!$PRP"] = stats["IT$!$PRP"] + it[key].proper_antecedent

    #stats["TP$!$NOM"] = 0
    #for key in third_person_plural.keys():
        #stats["TP$!$NOM"] = stats["TP$!$NOM"] + third_person_plural[key].nominal_antecedent
    #stats["TP$!$PRO"] = 0
    #for key in third_person_plural.keys():
        #stats["TP$!$PRO"] = stats["TP$!$PRO"] + third_person_plural[key].string_matches
    #stats["TP$!$PRP"] = 0
    #for key in third_person_plural.keys():
        #stats["TP$!$PRP"] = stats["TP$!$PRP"] + third_person_plural[key].proper_antecedent

    ## 6. same arg/diff arg/no arg pie graph
    ##stats["T$!$SAME_ARG"] = 0
    ##for key in third_person.keys():
    ##    stats["T$!$SAME_ARG"] = stats["T$!$SAME_ARG"] + third_person[key].pdtb["SAME_ARG"]
    ##stats["T$!$DIFF_ARG"] = 0
    ##for key in third_person.keys():
    ##    stats["T$!$DIFF_ARG"] = stats["T$!$DIFF_ARG"] + third_person[key].pdtb["DIFF_ARG"]
    ##stats["T$!$NONE"] = 0
    ##for key in third_person.keys():
    ##    stats["T$!$NONE"] = stats["T$!$NONE"] + third_person[key].pdtb["NONE"]

    ##stats["IT$!$SAME_ARG"] = 0
    ##for key in it.keys():
    ##    stats["IT$!$SAME_ARG"] = stats["IT$!$SAME_ARG"] + it[key].pdtb["SAME_ARG"]
    ##stats["IT$!$DIFF_ARG"] = 0
    ##for key in it.keys():
    ##    stats["IT$!$DIFF_ARG"] = stats["IT$!$DIFF_ARG"] + it[key].pdtb["DIFF_ARG"]
    ##stats["IT$!$NONE"] = 0
    ##for key in it.keys():
    ##    stats["IT$!$NONE"] = stats["IT$!$NONE"] + it[key].pdtb["NONE"]

    ##stats["TP$!$SAME_ARG"] = 0
    ##for key in third_person_plural.keys():
    ##    stats["TP$!$SAME_ARG"] = stats["TP$!$SAME_ARG"] + third_person_plural[key].pdtb["SAME_ARG"]
    ##stats["TP$!$DIFF_ARG"] = 0
    ##for key in third_person_plural.keys():
    ##    stats["TP$!$DIFF_ARG"] = stats["TP$!$DIFF_ARG"] + third_person_plural[key].pdtb["DIFF_ARG"]
    ##stats["TP$!$NONE"] = 0
    ##for key in third_person_plural.keys():
    ##    stats["TP$!$NONE"] = stats["TP$!$NONE"] + third_person_plural[key].pdtb["NONE"]

    ## 7. subj/obj ratio of antecedents
    #stats["T$!$SUBJ"] = 0
    #for key in third_person.keys():
        #stats["T$!$SUBJ"] = stats["T$!$SUBJ"] + third_person[key].subj
    #stats["T$!$OBJ"] = 0
    #for key in third_person.keys():
        #stats["T$!$OBJ"] = stats["T$!$OBJ"] + third_person[key].dobj
    ##stats["T$!$OTHER"] = 0
    ##for key in third_person.keys():
    ##    stats["T$!$OTHER"] = len(third_person[key].closest_antecedents) - stats["T$!$OBJ"] - stats["T$!$SUBJ"]

    #stats["IT$!$SUBJ"] = 0
    #for key in it.keys():
        #stats["IT$!$SUBJ"] = stats["IT$!$SUBJ"] + it[key].subj
    #stats["IT$!$OBJ"] = 0
    #for key in it.keys():
        #stats["IT$!$OBJ"] = stats["IT$!$OBJ"] + it[key].dobj
    ##stats["IT$!$OTHER"] = 0
    ##for key in it.keys():
    ##    stats["IT$!$OTHER"] = len(it[key].closest_antecedents) - stats["IT$!$OBJ"] - stats["IT$!$SUBJ"]

    #stats["TP$!$SUBJ"] = 0
    #for key in third_person_plural.keys():
    #    stats["TP$!$SUBJ"] = stats["TP$!$SUBJ"] + third_person_plural[key].subj
    #stats["TP$!$OBJ"] = 0
    #for key in third_person_plural.keys():
    #    stats["TP$!$OBJ"] = stats["TP$!$OBJ"] + third_person_plural[key].dobj
    #stats["TP$!$OTHER"] = 0
    #for key in third_person_plural.keys():
    #    stats["TP$!$OTHER"] = len(third_person_plural[key].closest_antecedents) - stats["TP$!$OBJ"] - stats["TP$!$SUBJ"]

    #make_bar_chart(DATASET, stats)
    #make_pie_graph(DATASET, pie_stats)

    ## Show result on screen
    #if "-plot" in sys.argv:
    #    show()
