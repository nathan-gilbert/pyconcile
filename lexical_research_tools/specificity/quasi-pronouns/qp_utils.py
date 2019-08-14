#!/usr/bin/python
# File Name : qp_utils.py
# Purpose :
# Creation Date : 01-07-2013
# Last Modified : Wed 26 Feb 2014 05:34:42 PM MST
# Created By : Nathan Gilbert
#
import sys
import re
import os

from pyconcile import utils
from pyconcile import data

DATASET="PROMED"
PROPER_NOUNS=[]
COMMON_NOUNS=[]
FIXES={}
CONCRETE_NOUNS={}

def set_dataset(ds):
    global DATASET
    DATASET = ds

def read_in_commons():
    global COMMON_NOUNS
    root = os.path.dirname(os.path.realpath(__file__))
    with open(root+"/{0}_COMMONS".format(DATASET), 'r') as commonFile:
        for line in commonFile:
            if line.startswith("#"): continue
            line=line.strip()
            COMMON_NOUNS.append(line)

def read_in_propers():
    global PROPER_NOUNS
    root = os.path.dirname(os.path.realpath(__file__))
    with open(root+"/{0}_PROPERS".format(DATASET), 'r') as properFile:
        for line in properFile:
            if line.startswith("#"): continue
            line=line.strip()
            PROPER_NOUNS.append(line)

def read_in_fixes():
    global FIXES
    root = os.path.dirname(os.path.realpath(__file__))
    with open(root+"/{0}_FIXES".format(DATASET), 'r') as fixFile:
        for line in fixFile:
            if line.startswith("#"): continue
            line = line.strip()
            sides = line.split("=>")
            FIXES[sides[0].strip()] = sides[1].strip()

def isProper(annot, pos):
    global PROPER_NOUNS
    if len(PROPER_NOUNS) < 1:
        read_in_propers()

    global COMMON_NOUNS
    if len(COMMON_NOUNS) < 1:
        read_in_commons()

    text = utils.textClean(annot.getText()).lower()
    if text in PROPER_NOUNS:
        return True

    if text in COMMON_NOUNS:
        return False
    if isPronoun(annot):
        return False
    if annot["DATE"] != "NONE":
        return False
    if text.find("http://") > -1 or text.find("www.") > -1:
        return False

    if annot["PROPER_NAME"] == "true" or annot["PROPER_NOUN"] == "true":
        return True

    tags = pos.getSubset(annot.getStart(), annot.getEnd())
    head = getHead2(text, tags)
    if isNumber(head):
        return False
    if head.endswith("%") or head.startswith("$"):
        return False
    if head in ("million", "billion", "cents", "dollars"):
        return False

    head = head.replace("\"","")
    head_span = getHeadSpan(annot, head)
    if head_span is None:
        head_span = getHeadSpan(annot, head.replace("]",""))
    pos_tag = pos.getAnnotBySpan(head_span[0], head_span[1])
    if pos_tag is None:
        return False
    if pos_tag["TAG"].startswith("NNP"):
        return True

    return False

def isNominal(annot, pos):
    """
    return True if the annotation is a nominal
    false otherwise
    """
    global PROPER_NOUNS
    if len(PROPER_NOUNS) < 1:
        read_in_propers()

    global COMMON_NOUNS
    if len(COMMON_NOUNS) < 1:
        read_in_commons()

    text = utils.textClean(annot.getText()).lower()
    if text in COMMON_NOUNS:
        return True

    if text in PROPER_NOUNS:
        return False

    if isPronoun(annot):
        return False

    if annot["DATE"] != "NONE":
        return False

    #remove websites
    if text.find("http://") > -1 or text.find("www.") > -1:
        return False

    if annot["PROPER_NAME"] == "true" or annot["PROPER_NOUN"] == "true":
        return False

    tags = pos.getSubset(annot.getStart(), annot.getEnd())
    head = getHead2(text, tags)

    #check if head is number
    if isNumber(head):
        return False
    if head.endswith("%") or head.startswith("$"):
        return False
    if head in ("million", "billion", "cents", "dollars"):
        return False

    #print text
    #print head
    #TODO: types of "word1 word2," causes problems
    head = head.replace("\"","")
    head_span = getHeadSpan(annot, head)
    if head_span is None:
        head_span = getHeadSpan(annot, head.replace("]",""))
    
    if head_span is not None:
        pos_tag = pos.getAnnotBySpan(head_span[0], head_span[1])
    else:
        return False

    if pos_tag is None:
        return False
    if pos_tag["TAG"].startswith("NNP"):
        return False

    return True

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def isPronoun(annot):
    text = utils.textClean(annot.getText()).lower().strip()
    if text in data.ALL_PRONOUNS:
        return True

    if text in ("here", "there", "then", "those"):
        return True
    return False

def getHead3(text):
    """uses the stanford nps"""
    pass

#TODO handle conjunctions
def getHead2(text, pos):
    """a more better head finding technique. """
    global FIXES
    if len(FIXES) < 1:
        read_in_fixes()

    if text in list(FIXES.keys()):
        return FIXES[text]

    left = []
    first = True
    for tag in pos:
        if tag["TAG"] in ("IN", "VBN", "VBP", "VBZ", "TO",
                "WDT", "WP") and not first:
            break
        left.append(tag)
        first = False
    tokens = text.split()[:len(left)]

    #remove commas from end of head
    first = True
    no_commas = []
    for tok in tokens:
        if tok.endswith(",") and not first:
            no_commas.append(tok[:-1])
            break
        first = False
        no_commas.append(tok)

    tokens = no_commas #list of words
    if len(tokens) > 0:
        #check if head is NNP
        #tags = pos[:len(tokens)]
        #if tags[-1]["TAG"].startswith("NNP"):
        #    tags.reverse()
        #    head = []
        #    i = len(tags) - 1
        #    for tag in tags:
        #        if tag["TAG"].startswith("NNP"):
        #            head.insert(0, tokens[i])
        #        i -= 1
        #    return removeBrackets(' '.join(head))
        #else:
        return removeBrackets(tokens[-1])
    else:
        return removeBrackets(text.split()[-1])

def removeBrackets(text):
    text = text.replace("(","").replace(")","")
    text = text.replace("[","").replace("]","")
    text = text.replace("{","").replace("}","")
    return text

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

