#!/usr/bin/python
# File Name : piecharter.py
# Purpose :
# Creation Date : 05-03-2013
# Last Modified : Wed 08 May 2013 10:58:09 AM MDT
# Created By : Nathan Gilbert
#
import sys
from pylab import *
from collections import defaultdict

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <piechart.stats>" % (sys.argv[0])
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
            if tokens[2] not in word_classes:
                word_classes.append(tokens[1])
            if tokens[3] not in stats:
                stats.append(tokens[2])

            stat2value["$!$".join(tokens[:-1])] = float(tokens[-1])

    #TODO: coalesce the values that are related into percentages.
    domains = {}
    for ds in datasets:
        values = defaultdict(list) #stat -> list of stat values across all domains
        for stat in stats:
            for w_cls in word_classes:
                values[stat].append(stat2value[ds+"$!$"+w_cls+"$!$"+stat])
        domains[ds] = values

    charts = ["TYPE", "PDTB", "FOCUS1"]
    i=1
    for ch in charts:
        # make a square figure and axes
        for ds in datasets:

            #these need to be the characteristic tag (Same Arg/Diff Arg, etc)
            labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'

            #these need to be the fraction for each of the labels above
            #fracs = [15, 30, 45, 10]
            fracs = []

            figure(1, figsize=(8,8))
            subplot(1,len(datasets),i)
            i+=1
            pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            title('blah')
    show()

