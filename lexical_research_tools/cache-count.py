#!/usr/bin/python
# File Name : cache-count.py
# Purpose :
# Creation Date : 03-11-2013
# Last Modified : Mon 11 Mar 2013 12:26:24 PM MDT
# Created By : Nathan Gilbert
#
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <cache-file>" % (sys.argv[0])
        sys.exit(1)

    counts = {}
    with open(sys.argv[1], 'r') as cacheFile:
        for line in cacheFile:
            line=line.strip()
            tokens = line.split("$!$")
            counts[tokens[1].strip()] = counts.get(tokens[1].strip(), 0) + 1

    for key in counts.keys():
        print "{0} : {1}".format(key, counts[key])
