#!/usr/bin/python
# File Name : utils.py
# Purpose : A repository of useful functions for use with pyconcile and related tools.
# Creation Date : 05-13-2011
# Last Modified : Fri 17 May 2013 09:31:20 AM MDT
# Created By : Nathan Gilbert
#
import string
import data

from collections import defaultdict

def spanInPrep(start, text):
    """Returns True is the given span is inside of a preposition, False o/w"""
    text = text.lower()
    prev_text = text[:start]
    tokens = prev_text.split()
    for t in tokens:
        if t in data.breakWords:
            return True
    return False

def spanInAppositive(start, text):
    """Returns True is the given span is on the right side of apposition, False o/w"""
    text = text.lower()
    prev_text = text[:start]
    tokens = prev_text.split()
    for t in tokens:
        if t.endswith(","):
            return True
    return False

def spanInHead(start, end, text):
    head_span = getTrueHeadSpan(text)
    if (start >= head_span[0] and end <= head_span[1]):
        return True
    return False

def getTextHead(text):
    tokens = text.split();
    new_text = "";
    first = True;
    for word in tokens:
        if word in data.breakWords and not first:
            break
        new_text += word + " "
        first = False
    new_text.strip()
    return new_text.split()[-1]

def isProper(text):
    """returns true if the text is a proper noun"""
    tokens = text.split()
    for word in tokens:
        if len(word) < 1: continue
        if (not word[0].isupper()):
            return False
    return True

def isConj(text):
    """returns true if noun phrase is a conjunction of two noun phrases"""
    if text.find(" and ") > -1:
        return True
    return False

def conjHead(text):
    tokens = text.split()
    found_and = False
    new_string = ""
    for word in tokens:
        if word == "and":
            found_and = True
        if (found_and and break_word(word)):
            break
        new_string += " " + word
    return new_string

def break_word(text):
    """returns true if text is a member of the break word list."""
    text = text.strip()
    if text in data.breakWords:
        return True
    return False

#TODO seems to be broken...
def getTrueHeadSpan(text):
    text = text.strip()
    #check if proper
    if isProper(text):
        return (0, len(text))

    #check if conjunction
    if isConj(text):
        new_text = conjHead(text)
        return (text.find(new_text), len(new_text))

    tokens = text.split()
    new_text = ""
    first = False
    start = -1
    end = -1
    for word in tokens:
        if (break_word(word) and not first):
            break
        if (word.endswith(",")):
            new_text += word[:-1]
            break

        #capture possessives?
        #if (word.endswith("'s"):
        #   new_text = ""
        #   continue

        new_text += word + " "
        first = False
    new_text = new_text.strip()
    if new_text == "":
        sys.err.write("Empty text: {0} : {1}".format(text, new_text))

    head = new_text.split()[-1]
    start = new_text.rfind(head)
    end = start + len(head)
    return (start, end)

def getTrueHead(text):
    """duplicates the head generation in java"""

    text = text.strip()
    #check if proper
    if isProper(text):
        return text

    #check if conjunction
    if isConj(text):
        return conjHead(text)

    tokens = text.split()
    new_text = ""
    first = False
    for word in tokens:
        if (break_word(word) and not first):
            break
        if (word.endswith(",")):
            new_text += word[:-1]
            break

        #capture possessives?
        #if (word.endswith("'s"):
        #   new_text = ""
        #   continue
        new_text += word + " "
        first = False
    new_text = new_text.strip()
    if new_text == "":
        sys.err.write("Empty text: {0} : {1}".format(text, new_text))
    return new_text.split()[-1]

def getFullText(directory):
    inFile = open(directory + "/raw.txt", 'r')
    allLines = ''.join(inFile.readlines())
    return allLines

def textClean(text):
    return ' '.join(map(string.strip, text.split())).strip()

def cleanPre(text):
    """
    removes determiners and demonstratives
    """
    if text.startswith("the ") \
            or text.startswith("his ")\
            or text.startswith("her ")\
            or text.startswith("our ")\
            or text.startswith("its "):
        text = text[4:]
    elif text.startswith("a "):
        text = text[1:]
    elif text.startswith("an "):
        text = text[2:]
    elif text.startswith("that ")\
        or text.startswith("this "):
        text = text[5:]
    elif text.startswith("their ")\
            or text.startswith("these "):
        text = text[6:]
    text = text.strip()
    return text

def remove_appositives(text):
    index = text.find(", ")
    if index > -1:
        return text[:index]
    return text

def remove_hard_pronouns(nps):
    """removes its, theys, thems, etc."""
    tmp = []
    for n in nps:
        if n.getATTR("text_lower") not in data.HARD_PRONOUNS:
            tmp.append(n)
    return tmp

def remove_its(nps):
    """Removes 'it's from a list of NPs"""
    tmp = []
    for n in nps:
        if (n.getATTR("text_lower") == "it") or (n.getATTR("text_lower") ==
                "its") or n.getATTR("it_is"):
            continue
        else:
            tmp.append(n)
    return tmp

def remove_i(nps):
    """Remove I from the set of nps provided."""
    tmp = []
    for n in nps:
        if n.getATTR("text_lower") in ("i","you","your"):
            continue
        else:
            tmp.append(n)
    return tmp

def remove_dates(nps):
    tmp = []
    for n in nps:
        if (n.getATTR("date") != "NONE"):
            continue
        else:
            tmp.append(n)
    return tmp

def remove_they(nps):
    """Removes they from a list of NPs"""

    tmp = []
    for n in nps:
        if (n.getATTR("text_lower") == "they") or (n.getATTR("text_lower") ==
            "their"):
            continue
        else:
            tmp.append(n)
    return tmp

def flatten(pairs):
    tmp=[]
    for p in pairs:
        if (type(p) == list):
            antecedent = p[0][0]
            anaphor = p[0][1]
            num=p[0][2]
        elif (type(p) == tuple):
            antecedent = p[0]
            anaphor = p[1]
            num=p[2]
        tmp.append((antecedent, anaphor, num))
    return tmp

def flattenText(text):
    """
    Takes a string and removes newlines
    """
    return text.replace("\n", " ")

def isDate(text):
    """Returns True if the text supplied contains a date, otherwise false """
    text=text.lower()
    if text in data.dates:
        return True
    return False

def match_nps(np_set1, np_set2):
    """ Match up gold annots with response annots"""
    for np1 in np_set1:
        for np2 in np_set2:
            if np1.getStart() == np2.getStart()  \
             and np1.getEnd() == np2.getEnd():
                np1.setProp("MATCHED", np2.getID())
                break
            elif np1.getATTR("HEAD_START") == np2.getStart() \
             and np1.getATTR("HEAD_END") == np2.getEnd():
                 np1.setProp("MATCHED", np2.getID())
                 break

def getConjunction(tok_tags):
    """
    return the conjunctions found in a set of tokens and tags
    """
    final_tt = tok_tags
    i = 0
    j = 0
    foundConj = False
    foundAnchor = False
    foundFirst = False
    for idx, tt in enumerate(tok_tags):
        #print tt,
        if tt[1].startswith("N") and not foundFirst:
            i = idx
            foundFirst = True
        elif tt[1] == "CC":
            j = idx
            foundConj = True
        elif foundConj and not foundAnchor and not tt[1].startswith("N"):
            j = idx
        elif foundConj and not foundAnchor and tt[1].startswith("N"):
            j = idx
            foundAnchor = True
        elif foundAnchor and tt[1].startswith("N"):
            j = idx
        elif foundAnchor and not tt[1].startswith("N"):
            #need one more for the slice operation to be correct
            j = idx
            break
    #print
    #print i,j
    return ' '.join(map(lambda x : x[0], final_tt[i:j]))

def getReconcileHead(text):
    """
    This function duplicates what Reconcile does in the lexical feature code
    for head matching.
    """
    tokens = text.split()
    new_text = ""
    first = True
    for word in tokens:
        if word in data.breakWords and not first:
            break
        if word[-1] == ',' and not first:
            new_text += word[:-1]
            break
        new_text += word + " "
        first = False
    new_text = new_text.strip()
    if new_text == "":
        return text

    head = new_text.split()[-1]
    if head[-1] == ',':
        return head[:-1]
    else:
        return head

def getReconcileCleanString(text):
    """
    This function attempts to 'clean up' a string in a way that leaves all
    modifiers that relate to the head, but removes any post-modifiers and
    clauses.
    """
    tokens = text.split()
    new_text = ""
    first = True
    for word in tokens:
        if word in data.breakWords and not first:
            break
        if word[-1] == ',' and not first:
            new_text += word[:-1]
            break
        new_text += word + " "
        first = False
    new_text = new_text.strip()
    if new_text == "":
        return text
    return ' '.join(new_text.split())

def getHead(annot):
    """
    Given an annotation, return the right most common noun or the full text of
    a proper name.

    Assumes the annotation has the "TAGS" and "TOKENS" properties.
    """
    head = []
    tok_tags = zip(annot.getATTR("TOKENS"), annot.getATTR("TAGS"))
    #print tok_tags

    if "CC" in map(lambda x : x[1], tok_tags):
        cc_head = getConjunction(tok_tags)
        #print cc_head
        return cc_head

    if len(tok_tags) == 1:
        return tok_tags[0][0]
    elif len(tok_tags) < 1:
        #some dates do not have a token nor tag?
        return annot.getText()

    #strip determiners
    i = 0
    for word in tok_tags:
        if not word[1].startswith("N") and word[1] != "CD":
            i += 1
        else:
            break
    head = tok_tags[i:]

    #stop at preps or relative clauses and pronouns
    i = 0
    for word in head:
        if word[1].startswith("N"):
            i += 1
        else:
            break
    head = head[:i]

    final_head = ""
    if all(map(lambda x : x[1].startswith("NNP"), head)):
        final_head = ' '.join(map(lambda x : x[0], head))
    elif head[-1][1] == "NNP":
        #the case where we have NN NNP "first-year Senator"
        i = 0
        for word in head:
            if word[1] not in ("NNP", "NNPS"):
                i += 1
                continue
            else:
                break
        final_head = ' '.join(map(lambda x : x[0], head[i:]))
    else:
        #the case where we have NNP NNP NN "Senator's assistant
        final_head = head[-1][0]

    if final_head == "":
        return annot.getText()
    else:
        return final_head

def getMods(annot):
    """
    Assumes the annotation has the "TAGS" and "TOKENS" properties.
    """
    #NOTE: this implementation pretty much ignores #s, right now for instances
    #$300 million, the head is "300 million"...
    head = []
    tok_tags = zip(annot.getATTR("TOKENS"), annot.getATTR("TAGS"))
    #print tok_tags

    if len(tok_tags) == 1:
        return ' '
    elif len(tok_tags) < 1:
        #some dates do not have a token nor tag?
        return ' '

    #strip determiners
    i = 0
    for word in tok_tags:
        if not word[1].startswith("N"):
            i += 1
            continue
        else:
            break
    head = tok_tags[i:]

    #stop at preps or relative clauses and pronouns
    i = 0
    for word in head:
        if word[1].startswith("N"):
            i += 1
            continue
        else:
            break
    head = head[:i]

    if all(map(lambda x : x[1].startswith("NNP"), head)):
        return ' '
    elif all(map(lambda x : x[1].startswith("NN"), head)):
        #return the case where we have multiple common nouns in a row, return
        #all modifiying common nouns
        return ' '.join(map(lambda x : x[0], head[:-1]))
    elif head[-1][1].startswith("NNP") and len(head) > 1:
        #the case where we have NN NNP "first-year Senator"
        i = 0
        for word in head:
            if not word[1].startswith("NNP"):
                i += 1
            else:
                break
        return ' '.join(map(lambda x : x[0], head[:i]))
    elif head[-1][1].startswith("NN") and len(head) > 1:
        #the case where we have NNP NNP NN "Senator's assistant
        i = 0
        for word in head:
            if word[1] not in ("NN", "NNS"):
                i += 1
            else:
                break
        return ' '.join(map(lambda x : x[0], head[:i]))
    else:
        return ' '

def sundance_hypernyms(tree_file):
    """
    Read in a sundance semtree and allow for topmost hypernyms
    """
    semtree = []
    with open(tree_file, 'r') as sem_tree_file:
        semtree.extend(sem_tree_file.readlines())
    sundance_semtree = []
    hypernyms = []
    depth = 0
    first = False
    cls = "";
    for line in semtree:
        #these are the classes we are not going to track
        if line.find("entity {") > -1:
                #or line.find("other {}") > -1 \
                #or line.find("animate {") > -1:
            continue
        line = line.replace("-", "_");
        if line.find("{}") > -1 and depth <= 0:
            sundance_semtree.append(line.replace("{}","").upper().strip())
            hypernyms = []
        elif line.find("{}") > -1 and depth > 0:
            sundance_semtree.append(":".join(hypernyms) + ":" + line.replace("{}","").upper().strip())
        elif line.find("{") > -1:
            hypernyms.append(line.replace("{","").upper().strip())
            depth += 1
        elif (line.find("}") > -1):
            depth -= 1
            if hypernyms != []:
                del hypernyms[-1]
    return sundance_semtree

if __name__ == "__main__":

    sun_hype = \
    sundance_hypernyms("/home/ngilbert/xspace/sundance-v5.1/data/semtree.txt")

    for path in sun_hype:
        print path
