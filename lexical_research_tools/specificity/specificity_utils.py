#!/usr/bin/python
# File Name : specificity_utils.py
# Purpose :
# Creation Date : 05-02-2013
# Last Modified : Tue 10 Dec 2013 10:51:00 AM MST
# Created By : Nathan Gilbert
#
import sys
import re

from pyconcile import utils
from pyconcile import data

PROPER_NOUNS=[]
COMMON_NOUNS=[]
CONCRETE_NOUNS={}

def read_in_propers():
    global PROPER_NOUNS
    #print "reading in proper names list"
    with open("/home/ngilbert/xspace/workspace/lexical-knowledge-base/specificity/proper_names", 'r') as properFile:
        for line in properFile:
            if line.startswith("#"): continue
            line=line.strip()
            PROPER_NOUNS.append(line)

def read_in_commons():
    global COMMON_NOUNS
    #print "reading in proper names list"
    with open("/home/ngilbert/xspace/workspace/lexical-knowledge-base/specificity/common_nouns", 'r') as commonFile:
        for line in commonFile:
            if line.startswith("#"): continue
            line=line.strip()
            COMMON_NOUNS.append(line)

def read_in_concreteness():
    global CONCRETE_NOUNS
    with open("/home/ngilbert/xspace/workspace/lexical-knowledge-base/specificity/quasi-pronouns/Concreteness_ratings_Brysbaert_et_al_BRM.txt", 'r') as inFile:
        for line in inFile:
            line=line.strip()
            tokens = line.split()
            if tokens[-1] == "Noun":
                value = float(tokens[2])
                CONCRETE_NOUNS[tokens[0]] = value

def getNounConcreteness(head):
    global CONCRETE_NOUNS
    if len(list(CONCRETE_NOUNS.keys())) < 1:
        read_in_concreteness()
    if head in list(CONCRETE_NOUNS.keys()):
        return CONCRETE_NOUNS[head]
    return -1.0

def isNominal(annot):
    """
    return True if the annotation is a nominal
    false otherwise
    """
    global COMMON_NOUNS
    if len(COMMON_NOUNS) < 1:
        read_in_commons()

    text = utils.textClean(annot.getText()).lower()
    if text in COMMON_NOUNS:
        return True

    if text.endswith("%"):
        return False

    if not isProper(annot) and text not in data.ALL_PRONOUNS and annot["DATE"] == "NONE":
        return True

    return False

def isPronoun(annot):
    text = utils.textClean(annot.getText()).lower().strip()
    if text in data.ALL_PRONOUNS:
        return True
    return False

def isProper(annot):
    global PROPER_NOUNS
    if len(PROPER_NOUNS) < 1:
        read_in_propers()

    text = utils.textClean(annot.getText()).lower().strip()
    if text in PROPER_NOUNS:
        return True

    if annot["PROPER_NAME"] == "true":
        return True
    if annot["PROPER_NOUN"] == "true":
        return True

    if text.startswith("mr."): return True
    if text.startswith("ms."): return True
    if text.startswith("mrs."): return True
    if text.endswith("corp."): return True
    if text.endswith("co."): return True
    if text.endswith("ltd."): return True
    if text.endswith("inc."): return True
    if text.endswith("ag"): return True
    if text.endswith("plc"): return True

    return False

def median(mylist):
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]

def getHead(text):
    """duplicates the head generation in java"""

    text = text.strip()
    #check if conjunction
    if utils.isConj(text):
        return utils.conjHead(text)

    tokens = text.split()
    new_text = ""
    first = True
    for word in tokens:
        if (utils.break_word(word) and not first):
            break

        if (word.endswith(",")):
            new_text += word[:-1]
            break

        new_text += word + " "
        first = False

    new_text = new_text.strip()
    if new_text == "":
        sys.stderr.write("Empty text: \"{0}\" : \"{1}\"".format(text, new_text))

    head = new_text.split()[-1]
    if head.endswith("'s"):
        head = head.replace("'s","")
    return head

def getHeadIndex(annot, head):
    annot_text = utils.textClean(annot.getText()).lower().strip()
    tokens = annot_text.split()
    i = 0
    for tok in tokens:
        if tok == head:
            return i
        i+=1
    return -1

def getHeadSpan(annot, head):
    head=head.replace("(","").replace(")","")
    match = re.compile(r'\b({0})\b'.format(head), flags=re.IGNORECASE).search(utils.textClean(annot.getText()))
    if match:
        return (match.start(1)+annot.getStart(), match.end(1)+annot.getStart())
    return None

