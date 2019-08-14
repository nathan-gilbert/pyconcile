#!/usr/bin/python
"""
File Name : /home/nathan/.workspace/pyconcile-tools/src/pyconcile/pronoun_heuristics.py
Purpose :
Creation Date : May 13, 2011
Last Modified : Wed 01 Jun 2011 03:08:36 PM MDT
@author: nathan
"""

from collections import defaultdict
from operator import itemgetter

import reconcile
import data
import string_match

def heuristic1(nps, p):
    """first person in same/prev sentence"""

    nps.reverse()
    pairs = []
    for np in nps:
        #make sure to enforce the ordering constraints and that the referent
        #and antecedent cannot be the same entity.
        if (np > p) or (np == p):
            continue

        #the np and pronoun match in gender and number
        if data.gender_agreement(np.getATTR("gender"), p.getATTR("gender")) \
        and data.number_agreement(np.getATTR("number"), p.getATTR("number"))\
        and data.semantic_agreement(np, p):
            pairs.append((np,p,"1"))
            break

    return pairs

def heuristic2(nps, p):
    """Possessive equivalent of hueristic1"""
    nps.reverse()
    pairs=[]
    for np in nps:
        if (np > p) or (np == p):
            continue

        if (data.gender_agreement(np.getATTR("gender"), p.getATTR("gender"))) \
        and (data.number_agreement(np.getATTR("number"), p.getATTR("number"))):
            pairs.append((np,p,"2"))
            break

    return pairs

def heuristic3(text,nps,p):
    """Resolving I,we,ours,us to X said."""

    pairs=[]
    for np in nps:
        #make sure the np
        if (np > p):
            s = "%s said" % np.getText()
            if (text.find(s) > p.getEnd()) \
            and data.number_agreement(p.getATTR("number"),
                    np.getATTR("number")) \
            and data.gender_agreement(p.getATTR("gender"),
                    np.getATTR("gender")):
                pairs.append((p,np,"3"))
                break
    return pairs

def heuristic4(nps, poss):
    """Possessive/Pro from Cogniac"""

    pairs = []
    for i in range(0, len(poss)):
        nextNP = reconcile.nextNP(nps, poss[i])
        try:
            text_i = "%s %s" % (poss[i].getATTR("text_lower"),
                    nextNP.getATTR("text_lower"))
        except:
            continue

        for j in range(i+1, len(poss)):
            jNP = reconcile.nextNP(nps, poss[j])
            try:
                text_j = "%s %s" % (poss[j].getATTR("text_lower"),
                        jNP.getATTR("text"))
            except:
                continue

            if text_i == text_j:
                #print text_i
                #print text_j
                pairs.append((poss[i], poss[j],"4"))
    return pairs

def heuristic5(sents, pronouns):
    """Unique Subject from Cogniac"""

    pairs=[]
    for i in range(1, len(pronouns)):
        p = pronouns[i]
        if p.getATTR("grammar") == "SUBJECT":
            prevP = pronouns[i-1]
            prevS = reconcile.prev_sent(sents, p)
            if reconcile.NPinS(prevP, prevS) \
            and (prevP.getATTR("grammar") == "SUBJECT") \
            and string_match.head_match(prevP.getText(), p.getText(), False):
                pairs.append((prevP,p,"5"))
    return pairs

def heuristic6(nps, p):
    """first person in same/prev sentence, a less strict version of H:1"""
    nps.reverse()
    pairs = []
    for np in nps:
        if (np > p) or (np == p):
            continue
        if data.gender_agreement(np.getATTR("gender"), p.getATTR("gender")):
            pairs.append((np,p,"6"))
            #find the first one then go on to the next pronoun
            break
    return pairs

def heuristic7(nps, p):
    """Possessive equivalent of hueristic1, a less strict version of H:2"""

    nps.reverse()
    pairs=[]
    for np in nps:
        if (np > p) or (np == p):
            continue
        if (data.gender_agreement(np.getATTR("gender"), p.getATTR("gender"))):
            pairs.append((np,p,"7"))
            break
    return pairs

def heuristic8(nps,pronouns):
    """Find the Proper Name that has been mentioned the most in the document, and then find any pronouns that
    are not resolved to anything and match them if gender and number match. """

    pairs=[]
    entities={}
    properties=defaultdict(list)

    for n in nps:
        if n.getATTR("proper_name") != "NONE":
            text=n.getATTR("text_lower")
            entities[text] = entities.get(text, 0) + 1
            properties[text].append(n)

    #finding the most common proper name
    e_sorted = sorted(entities.items(), key=itemgetter(1), reverse=True)
    try:
        top = e_sorted[0][0]
    except:
        return pairs

    np = None
    for p in pronouns:
        #first make sure the pronoun is not before the np in the document.
        for n in properties[top]:
            if (p.getStart() < n.getStart()):
                continue
            else:
                np = n

                #check for number and gender agreement
                if data.gender_agreement(p.getATTR("gender"),np.getATTR("gender"))\
                and data.number_agreement(p.getATTR("number"),np.getATTR("number"))\
                and data.semantic_agreement(p,np):
                    pairs.append((np,p,"8"))
    return pairs

