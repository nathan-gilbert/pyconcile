#!/usr/bin/python
# File Name : utils.py
# Purpose :
# Creation Date : 06-25-2012
# Last Modified : Wed 27 Jun 2012 10:57:45 AM MDT
# Created By : Nathan Gilbert
#
import sys
import nltk

# Extract phrases from a parsed (chunked) tree
# Phrase = tag for the string phrase (sub-tree) to extract
# Returns: List of deep copies;  Recursive
def extract_phrases(myTree, phrase):
    myPhrases = []
    if (myTree.node == phrase):
        myPhrases.append(myTree.copy(True))
    for child in myTree:
        if (type(child) is nltk.Tree):
            list_of_phrases = extract_phrases(child, phrase)
            if (len(list_of_phrases) > 0):
                myPhrases.extend(list_of_phrases)
    return myPhrases

def isDefinite(text):
    if np_tokens[0].lower() in ("the"):
        return True
    else:
        return False
    return False

def isIndefinite(text):
    if np_tokens[0].lower() in ("a", "an"):
        return True
    else:
        return False
    return False


