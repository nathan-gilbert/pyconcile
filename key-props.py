#!/usr/bin/python
# File Name : key-props.py
# Purpose :
# Creation Date : 10-29-2013
# Last Modified : Tue 29 Oct 2013 03:00:37 PM MDT
# Created By : Nathan Gilbert
#
import sys
import re

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <npProps>" % (sys.argv[0])
        sys.exit(1)

    SEM = re.compile('.*NPSemanticType=\"([^"]*)\".*')
    GEN = re.compile('.*Gender=\"([^"]*)\".*')
    NUM = re.compile('.* Number=\"([^"]*)\".*')
    TEXT = re.compile('.*Text=\"([^"]*)\".*')

    with open(sys.argv[1], 'r') as propsFile:
        for line in propsFile:
            props = {}
            line = line.strip()
            tokens = line.split()

            start = int(tokens[1].split(",")[0])
            end = int(tokens[1].split(",")[1])

            numMatch = NUM.match(line)
            if numMatch:
                num = numMatch.group(1)
                props['NUMBER'] = num
            else:
                props['NUMBER'] = "UNKNOWN"

            match = GEN.match(line)
            if match:
                g = match.group(1)
                props["GENDER"] = g
            else:
                props["GENDER"] = "UNKNOWN"

            match = SEM.match(line)
            if match:
                s = match.group(1)
                props["SEMANTIC"] = s
            else:
                props["SEMANTIC"] = "UNKNOWN"

            match = TEXT.match(line)
            if match:
                text = match.group(1)

            print "{0} ({1},{2})\n{3}\t{4}\t{5}".format(text, start, end, num, g, s)
