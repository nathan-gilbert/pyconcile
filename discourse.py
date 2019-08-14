#!/usr/bin/python
# File Name : discourse.py
# Purpose : A set of methods looking at discourse characteristics from
#           Reconcile output. 
# Creation Date : 08-26-2011
# Last Modified : Fri 26 Aug 2011 05:41:18 PM MDT
# Created By : Nathan Gilbert
#
import sys
import nltk

from . import reconcile
from .document import Document

#TODO from Allen pg. 507 
def sentence_segment(sent):
    """return a list containing the segments found in this sentence."""

#TODO: Read something on this...and figure out what it should be...
def focus_shift( ):
    """  """

if __name__ == "__main__":
    #test some feature of this code

    inFile = open("/home/ngilbert/xspace/data/ace2v1-npaper-train/0/raw.txt",
            'r')
    rawTxt = ''.join(inFile.readlines())
    inFile.close()

    tokens = texttiles(rawTxt)
    for t in tokens:
        print("=============")
        print((t.strip()))
        print("=============")

