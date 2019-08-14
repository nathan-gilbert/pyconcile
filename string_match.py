#!/usr/bin/python
# File Name : string_match.py
# Purpose : Provide functionality on various types of string match.
# Creation Date : 05-10-2011
# Last Modified : Tue 08 May 2012 02:10:28 PM MDT
# Created By : Nathan Gilbert
#
import sys
import re
import string

import nltk
import nltk.metrics.distance

from pyconcile import annotation
from pyconcile import data

NUMBERS = re.compile('^[0-9 ]+')

def getHead(text):
    """Returns the right most non-punctuation token of a string."""

    if text.strip() == "":
        return ""

    tokens = text.split()
    tokens.reverse()
    for t in tokens:
        if t.strip() in string.punctuation:
            continue
        elif t == "'s":
            continue
        else:
            return t.strip()

    return tokens[-1]

def isHead(full_string, head):
    """Returns True if the supplied head is actually the head of the string
    supplied."""
    true_head = getHead(full_string)
    if sub_string(head, true_head):
        return True
    return False

def exact_match(text1, text2, case=True):
    """ Returns True if the two strings match perfectly. set case to False to ignore case """

    if case and (text1 == text2):
        return True
    elif not case and (text1.lower() == text2.lower()):
        return True
    else:
        return False

def sub_string(sub, sup, case=True):
    """ Returns True if sub is a proper substring of sup, else False """

    if not case:
        sup = sup.lower()
        sub = sub.lower()

    if sup.find(sub) > -1:
        return True
    else:
        return False

    return False

def word_overlap(sub, sup, case=True):
    """Returns true if sub overlaps with sup perfectly. False otherwise"""

    if not case:
        sub = sub.lower()
        sup = sup.lower()

    index = sup.find(sub)
    if index > -1:
        L = len(sub)
        if (L + index) < len(sup):
            ch = sup[index + L]
            if (ch == ' ') or (ch in string.punctuation):
                return True
        else:
            return True
    return False

def head_match(text1, text2, case=True):
    """ Returns True if the heads (the rightmost token) match exactly. """

    #head1 = text1.split()[-1]
    head1 = getHead(text1)
    #head2 = text2.split()[-1]
    head2 = getHead(text2)

    return exact_match(head1, head2, case)

def soon_match(text1, text2, case=True):
    """ After discarding determiners, do the strings still match? """
    soon_string1 = remove_titles(remove_determiners(text1))
    soon_string2 = remove_titles(remove_determiners(text2))
    return exact_match(soon_string1, soon_string2, case)

def remove_determiners(text):
    """Remove determiners from the given text."""
    global NUMBERS
    #remove #'s
    new_text = re.sub(NUMBERS, '', text)

    tokens = new_text.split()
    for t in tokens:
        if (t.lower() in data.reconcile_determiners):
            tokens.remove(t)
    new_text = ' '.join(tokens)
    return new_text

def remove_titles(text):
    tokens = text.split()
    for t in tokens:
        if (t.lower() in data.titles):
            tokens.remove(t)
    new_text = ' '.join(tokens)
    return new_text

def isAcronym(text1, text2):
    """returns true if text2 is an acronym of text1"""

    text1_nodets = remove_determiners(text1)
    text2_nodets = remove_determiners(text2)

    tokens1 = text1.split()
    new_text = ''.join([x[0] for x in tokens1])

    if new_text == text2:
        return True

def word_overlap_count(text1, text2, case=True):
    """Return the percentage of word overlap between the two texts."""
    #TODO: 
    pass

def edit_dist(text1, text2):
    """Returns the edit distance """
    return nltk.metrics.distance.edit_distance(text1, text2)

def guantlet(text1, text2):
    """ Passes the texts through a series of matches to see if
    there is but a hint of string-matchyness"""

    text1 = remove_determiners(text1)
    text2 = remove_determiners(text2)

    if sub_string(text1, text2, False) \
        or sub_string(text2, text1, False):
        return True
    elif head_match(text1, text2, False):
        return True
    elif sub_string(getHead(text1), text2, False) \
        or sub_string(text1, getHead(text2), False) \
        or sub_string(getHead(text1), getHead(text2), False) \
        or sub_string(text2, getHead(text1), False) \
        or sub_string(getHead(text2), text1, False) \
        or sub_string(getHead(text2), getHead(text1), False):
        return True
    elif word_overlap(text1, text2, False) > 2:
        return True
    else:
        porter = nltk.PorterStemmer()
        stem1 = [porter.stem(t) for t in text1.split()]
        stem2 = [porter.stem(t) for t in text2.split()]
        for t in stem1:
            if t in stem2:
                return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(("Usage: %s <first-argument>" % (sys.argv[0])))
        sys.exit(1)

