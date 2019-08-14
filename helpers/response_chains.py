#!/usr/bin/python
# File Name : response_chains.py
# Purpose : Prints out the response chains
# Creation Date : 08-08-2011
# Last Modified : Tue 04 Jun 2013 10:11:51 AM MDT
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <dir> <outfile>" % (sys.argv[0]))
        sys.exit(1)

    base_dir = sys.argv[1]
    cluster_file = sys.argv[2]

    response_chains = reconcile.getResponseChains(base_dir, cluster_file)

    for k in list(response_chains.keys()):
        if len(response_chains[k]) > 1:
            print("{ ", end=' ')
            print("%s" % (" \n\t<- ".join([x.ppprint() for x in response_chains[k]])), end=' ')
            print("\n}")


