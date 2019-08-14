#!/usr/bin/python
# File Name : barcharter.py
# Purpose :
# Creation Date : 05-03-2013
# Last Modified : Wed 08 May 2013 10:49:12 AM MDT
# Created By : Nathan Gilbert
#
import sys
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from collections import defaultdict

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),ha='center', va='bottom')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <barchart-file>" % (sys.argv[0])
        sys.exit(1)

    stat2value = {}
    datasets = []
    word_classes = []
    stats = []
    with open(sys.argv[1], 'r') as inFile:
        for line in inFile:
            line=line.strip()
            tokens = line.split("$!$")
            if tokens[0] not in datasets:
                datasets.append(tokens[0])
            if tokens[1] not in word_classes:
                word_classes.append(tokens[1])
            if tokens[2] not in stats:
                stats.append(tokens[2])

            stat2value["$!$".join(tokens[:-1])] = float(tokens[-1])

    N = len(word_classes)
    #N = len(datasets)
    ind = np.arange(N) # the x locations for the groups
    width = 0.10       # the width of the bars
    colors = ('r','b','g','y','p')

    domains = {}
    for ds in datasets:
        values = defaultdict(list) #stat -> list of stat values across all domains
        for stat in stats:
            for w_cls in word_classes:
                values[stat].append(stat2value[ds+"$!$"+w_cls+"$!$"+stat])
        domains[ds] = values

    for stat in stats:
        if stat == "WORD_STD":continue
        fig = plt.figure(figsize=(8,8),dpi=150)
        ax = fig.add_subplot(111)
        rects = []
        for w_cls in word_classes:
            i=0
            gap=0
            for ds in domains.keys():
                if not stat.startswith("WORD") :
                    rect = ax.bar(ind+gap, domains[ds][stat], width, color=colors[i])
                elif stat.startswith("WORD_MEAN"):
                    rect = ax.bar(ind+gap, domains[ds][stat], width, color=colors[i], yerr=domains[ds]["WORD_STD"])
                else:
                    continue
                rects.append(rect[0])
                i+=1
                gap+=width

        # add some
        ax.set_ylabel('Count')
        ax.set_title('{0} across domains'.format(stat))
        ax.set_xticks(ind+width)
        ax.set_xticklabels(word_classes)

        rects = rects[:len(datasets)]
        if len(rects) < 1: continue
        ax.legend(rects, datasets, loc="upper right")

        savefig("{0}.png".format(stat.lower()), dpi=150)
        #autolabel(rects1)
        #autolabel(rects2)
    plt.show()
