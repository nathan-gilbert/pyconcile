#!/usr/bin/python
#
import sys
import re
#from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <features-file> <npProperties-file>" % (sys.argv[0])
        sys.exit(1)

    NO = re.compile('.*NO=\"([^"]*)\".*')
    ID = re.compile('.*ID=\"([^"]*)\".*')
    TEXT = re.compile('.*Text=\"([^"]*)\".*')
    BYTES = re.compile('.*\s+(\d+),(\d+)\s+.*')

    pairs = []
    featuresFile = open(sys.argv[1], 'r')
    for line in featuresFile:
        line = line.strip()

        if line == '' or line.startswith("@"):
            continue
        else:
            tokens = line.split(",")
            if tokens[-1] == "+":
                coref = True
            else:
                coref = False
            pairs.append((int(tokens[1]),int(tokens[2]), coref))
    featuresFile.close()

    npsFile = open(sys.argv[2], 'r')
    nps = {}
    npBytes = {}
    for line in npsFile:
        line = line.strip()
        if line.startswith("#"):
            continue

        match = NO.match(line)
        if match:
            npNum = int(match.group(1))
        match = TEXT.match(line)
        if match:
            npText = match.group(1)

        match = BYTES.match(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))

        nps[npNum] = npText
        npBytes[npNum] = (start,end)

    #nps.keys().sort()
    #for k in nps.keys():
        #print "%s : %s" % (k, nps[k])

    for p in pairs:
        print "%s (%d,%d) : %s (%d,%d) : %s" % (nps[p[0]], npBytes[p[0]][0], npBytes[p[0]][1], nps[p[1]], npBytes[p[1]][0], npBytes[p[1]][1], p[2])


