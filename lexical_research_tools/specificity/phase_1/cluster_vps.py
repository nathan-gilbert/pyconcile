#!/usr/bin/python
# File Name : cluster_vps.py
# Purpose :
# Creation Date : 07-17-2013
# Last Modified : Mon 22 Jul 2013 12:29:55 PM MDT
# Created By : Nathan Gilbert
#
import sys
from nltk import cluster
from nltk.cluster import euclidean_distance
from numpy import array
from collections import defaultdict

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <vp-file>" % (sys.argv[0]))
        sys.exit(1)

    heads = []
    heads2values = {}
    values = []
    key = []
    with open(sys.argv[1], 'r') as headFile:
        for line in headFile:
            if line.startswith("#"): continue

            if line.startswith("head"):
                print("first line {0}".format(line))
                tokens = line.split()
                key = tokens[5:]
                del key[5]
                del key[-2]
                del key[-3]
                del key[1]

                tmp = []
                for k in key:
                    if len(k) == 2:
                        new_k = " {0} ".format(k)
                    elif len(k) == 3:
                        new_k = " {0}".format(k)
                    elif len(k) == 4:
                        new_k = k
                    tmp.append(new_k)
                key = tmp

                continue

            line = line.strip()
            if line == "": continue #skip blank lines
            tokens = line.split()
            v = [float(x) for x in tokens[5:]]

            del v[5] #remove ss
            del v[-2] #remove aidf
            del v[-3] #remove aidf
            del v[1]
            heads.append(tokens[0])
            heads2values[tokens[0]] = v
            values.append(v)

    #print len(heads)
    #print len(values)
    print(key)
    #print heads
    #print values
    vectors = [array(f) for f in values]
    clusterer = cluster.KMeansClusterer(3, euclidean_distance)
    clusters = clusterer.cluster(vectors, True)
    print(clusters)
    #print len(clusters)
    #print vectors

    cluster2head = defaultdict(list)
    for i in range(0, len(clusters)):
        head = heads[i]
        cl = clusters[i]
        cluster2head[cl].append(head)

    for cl in list(cluster2head.keys()):
        print("Cluster: {0}".format(cl))
        print("{0:31} {1}".format("head", key))
        for head in cluster2head[cl]:
            s = ["{0:4.2f}".format(x) for x in heads2values[head]]
            print("\t{0:20} => {1}".format(head, s))
        print()
