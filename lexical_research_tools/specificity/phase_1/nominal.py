#!/usr/bin/python
# File Name : nominal.py
# Purpose :
# Creation Date : 07-16-2013
# Last Modified : Wed 17 Jul 2013 10:00:03 AM MDT
# Created By : Nathan Gilbert
#
import sys

class Nominal:
    def __init__(self, t):
        #basic
        self.head               = ""
        self.count              = 1
        self.texts              = []
        self.docs               = []
        self.closest_antecedent = []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <first-argument>" % (sys.argv[0]))
        sys.exit(1)


