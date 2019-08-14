#!/usr/bin/python
# File Name : score.py
# Purpose : Script implementing many coreference scoring and agreement metrics
# Creation Date : 10-01-2010
# Last Modified : Tue 04 Jun 2013 10:19:30 AM MDT
# Created By : Nathan Gilbert
import numpy
from collections import defaultdict

import reconcile
from annotation import Annotation

def print_matching_nps(annots1, annots2):
    match_nps(annots1, annots2)
    matched=0
    unmatched=0
    for a in annots2:
        if a.getATTR("MATCHED") > -1:
            print "%d -> %d MATCHED" % (a.getID(), a.getATTR("MATCHED"))
            matched+= 1
        else:
            print "%d -> %d NOT-MATCHED" % (a.getID(), a.getATTR("MATCHED"))
            unmatched+=1

def spanMatch(a1, a2):
    """Returns True if a2 is inside the span of a1 """

    if (a2.getStart() >= a1.getStart()) and (a2.getEnd() <= a1.getEnd()):
        return True
    return False

def minMatch(a1, a2):
    """Returns true if a2's min is inside the span of a1"""
    if (a2.getATTR("MIN") == ""):
        #we don't know anything about it since there is no specified
        return False
    else:
        if (a1.getText().find(a2.getATTR("MIN")) > -1) and spanMatch(a1, a2):
            return True
    return False

def exactMatch(a1, a2):
    if a1 == a2:
        return True
    else:
        return False

def needsExact(a):
    """If the HEAD span equals the maximal span returns True"""
    if (a.getStart() == a.getATTR("HEAD_START")) \
            and (a.getEnd() == a.getATTR("HEAD_END")):
        return True
    else:
        return False

def headMatch(a1, a2):
    """Returns true if a2's head is inside the span of a1."""
    if (a1.getATTR("HEAD_START") < 0 or a1.getATTR("HEAD_END") < 0):
        return False
    elif (a2.getATTR("HEAD_START") < 0 or a2.getATTR("HEAD_END") < 0):
        return False
    elif needsExact(a1):
        #if the gold head matches the gold max span, then require an exact
        #match on the response side.
        return False
    else:
        #if we don't need an exact match, then both annots have HEADS. 
        #the response annot needs to be at least the same as the gold head, but
        #not bigger than the entire span (which should be caught by spanMatch()
        if (a2.getATTR("HEAD_START") >= a1.getATTR("HEAD_START")) \
                and (a2.getATTR("HEAD_END") >= a1.getATTR("HEAD_END")):
            return True
    return False

def onlyDifferenceIsDeterminer(a1, a2):
    """if the only difference between the gold head and the response head is a determiner,
    then allow it"""
    if a2.getText().startswith("The ") \
            or a2.getText().startswith("the "):
        new_start = a2.getStart()+4
    elif a2.getText().startswith("A ") \
            or a2.getText().startswith("a "):
        new_start = a2.getStart()+2
    elif a2.getText().startswith("This ") \
            or a2.getText().startswith("this "):
        new_start = a2.getStart()+5
    else:
        new_start = a2.getStart()

    if new_start == a1.getATTR("HEAD_START") \
            and a2.getATTR("HEAD_END") == a1.getATTR("HEAD_END")\
            and a2.getEnd() <= a1.getEnd():
        return True
    else:
        return False

def mucMatching(a1, a2):
    """Corresponds to the MUC guidelines in matching two nominals"""
    if exactMatch(a1, a2):
        return True
    elif spanMatch(a1, a2) and (minMatch(a1, a2) or headMatch(a1,a2)):
        return True
    elif onlyDifferenceIsDeterminer(a1, a2):
        return True
    else:
        return False
    return False

def match_nps(gold, response):
    """matches the nps in the response with the nps in the gold set."""
    #don't allow double matching
    #matched = []
    for r_np in response:
        r_np.setProp("MATCHED", -1)

    for r_np in response:
        for g_np in gold:
            #if the maximal span of the response is inside the maximal span of
            #the gold and the minimal span of the response is at least the head
            #of the gold
            if mucMatching(g_np, r_np): #and (g_np.getID() not in matched):
                r_np.setProp("MATCHED", g_np.getID())
                #matched.append(g_np.getID())

def equivalence_classes(annots):
    """Returns a dict of equivalence classes of annotations."""
    classes = defaultdict(list)
    num = 0
    for a in annots:
        classes[a.getATTR("COREF_ID")].append(a)
    return classes

def print_equiv_classes(gold, response):
    gold_equiv = equivalence_classes(gold)
    g = ""
    for c in gold_equiv.keys():
        g += "{"
        for mention in gold_equiv[c]:
            #g = g + mention.getATTR("LETTER") + ","
            g = g + mention.getATTR("ID") + ","
        if g[-1] == ",":
            g = g[:-1]
            g+="}"
    print "Gold: " + g

    response_equiv = equivalence_classes(response)
    r = ""
    for c in response_equiv.keys():
        r += "{"
        for mention in response_equiv[c]:
            #r = r + mention.getATTR("LETTER") + ","
            r = r + mention.getATTR("ID") + "(" + \
            str(mention.getATTR("MATCHED")) \
            +")" + ","
        if r[-1] == ",":
            r = r[:-1]
            r+="}"
    print "Response: " + r

def accuracy(gold, response):
    """
    Simple anaphor accuracy. Returns the %% of resolutions made that are correct.
    The response in this case is pairs, not chains
    """
    correct = 0
    for pair in response:
        antecedent = pair[0]
        anaphor = pair[1]
        for key in gold.keys():
            chain = gold[key]
            foundAntecedent = False
            foundAnaphor = False
            for mention in chain:
                if mucMatching(mention, antecedent):
                    foundAntecedent = True
                if mucMatching(mention, anaphor):
                    foundAnaphor = True
            if foundAntecedent and foundAnaphor:
                correct += 1
                break
    try:
        return (correct, len(response), float(correct) / len(response))
    except ZeroDivisionError:
        return (correct, len(response), 0.0)

def correctpair(gold, antecedent, anaphor):
    correct = 0
    for key in gold.keys():
        chain = gold[key]
        foundAntecedent = False
        foundAnaphor = False
        for mention in chain:
            if mucMatching(mention, antecedent):
                foundAntecedent = True
            if mucMatching(mention, anaphor):
                foundAnaphor = True
        if foundAntecedent and foundAnaphor:
            return True
    return False

def total_possible_links(annots1, annots2):
    match_nps(annots1, annots2)

    s1 = filter(lambda x : x >= 0, map(lambda x : \
        x.getATTR("MATCHED"), annots2))
    s2 = map(lambda x : x.getID(), annots1)
    matches = len(s1) #the number of overlapping nps
    not_matched1 = len(list(set(s2) - set(s1))) #the number of nps in 1
    not_matched2 = len(filter(lambda x : int(x.getATTR("MATCHED")) < 0, annots2))
    return matches + not_matched1 + not_matched2 - 1

def compute_d(annots1, annots2):
    d = 0
    equiv1 = equivalence_classes(annots1)
    equiv2 = equivalence_classes(annots2)
    match_nps(annots1, annots2)
    pCA = defaultdict(list)
    ids_not_matched = map(lambda x : x.getID(), annots1)
    for k in equiv2.keys():
        for mention in equiv2[k]:
            if mention.getATTR("MATCHED") == -1:
                #if it isn't matched, it's already it's own cluster
                pCA[str(-int(mention.getATTR("ID")))].append(mention)
            else:
                if int(mention.getATTR("MATCHED")) in ids_not_matched:
                    ids_not_matched.remove(int(mention.getATTR("MATCHED")))
                index = mention.getATTR("COREF_ID")
                pCA[index].append(mention)

    #the intersection between CA1 & pCA
    CA1_pCA = defaultdict(list)
    match = 0
    for k in equiv1.keys():
        ids = map(lambda x : int(x.getATTR("ID")), equiv1[k])

        for k2 in pCA.keys():
            ids2 = map(lambda x : x.getATTR("MATCHED"), pCA[k2])

            if set(ids) == set(ids2):
                #print ids2
                CA1_pCA[match].extend(pCA[k2])
                match+=1

    #gather all the things that were not in CA
    for k in pCA.keys():
        if int(k) > 0:
            continue
        if len(pCA[k]) == 1 and pCA[k][0].getATTR("MATCHED") == -1:
            #print "%s: %d (%s)" % (k, pCA[k][0].getID(), pCA[k][0].getATTR("MATCHED"))
            CA1_pCA[match].extend(pCA[k])
            match+=1
    d1 = len(CA1_pCA.keys()) - 1
    return float(d1)

def vilain_num(gold, response):
    """ The MUC Score numerator """
    match_nps(gold, response)
    gold_equiv = equivalence_classes(gold)

    total_num = 0.0
    for k in gold_equiv.keys():
        #this is the cardinality of this partition in the gold chain
        C = len(gold_equiv[k])

        #first get all the nps that match nps in this gold chain
        matched_nps = [mention for mention in response if \
                mention.getATTR("MATCHED") in \
                map(lambda x : x.getID(), gold_equiv[k])]
        matched_np_ids = map(lambda x : x.getATTR("COREF_ID"), matched_nps)

        #the number of different ids in the response set is the number of
        #'links' needed to make the response look like the gold.
        pC = len(set(matched_np_ids))

        #find the # of NPs from the gold that are NOT matched by any resp np.
        missed_gold = len(gold_equiv[k]) - len(matched_nps)

        total_num += (C - pC - missed_gold)
    return float(total_num)

def vilain_denom(gold):
    """The MUC Denominator """
    gold_equiv = equivalence_classes(gold)
    total_denom = 0.0
    for k in gold_equiv.keys():
        #this is the cardinality of this partition in the gold chain
        C = len(gold_equiv[k])
        total_denom += (C - 1)
    return float(total_denom)

def vilain_helper(gold, response):
    return vilain_num(gold, response) / vilain_denom(gold)

def vilain(gold, response):
    """
    Implementation of the MUC scoring metric.
    A model theoretic coreference scoring scheme - Vilain et al. (1995)
    """
    recall = vilain_helper(gold, response)
    #to ensure the same matching in both directions
    precision = vilain_num(gold, response) / vilain_denom(response)

    #get the fmeasure
    f_m = f(recall, precision)
    return (precision, recall, f_m)

def bcubed(gold, response):
    """Implementation of the B^3 scoring metric. """
    #TODO
    pass

def bcubed_notwins(gold, response):
    """ Implementation of B^3 metric ignoring non-twins in the gold/response """
    #TODO
    pass

def ceaf(gold, response):
    """TODO: Implementation of CEAF metrics """
    pass

def blanc(gold, response):
    """Implementation of the BLANC scoring metric. """
    #TODO: 
    pass

def kappa(annots1, annots2):
    """
    Implements the kappa annotator agreement score metric for coreference. annots1 by annots2
    """
    a = vilain_num(annots1, annots2)
    b = vilain_denom(annots2) - a
    c = vilain_denom(annots1) - a
    #d = compute_d(annots1, annots2) #not working as well as just collecting
                                     #all possible links (which is computationally 
                                     #easier as well.)
    d = total_possible_links(annots1, annots2) - a - b - c
    e = a + b + c + d

    #print "e:%d = a:%d - b:%d - c:%d - d:%d" % (e, a, b, c, d)
    #coincidence_matrix = numpy.matrix([[a,b],[c,d]])
    #print coincidence_matrix

    pAo = (a / e) + (d / e)
    pAe = ((a + c) / e)**2 + ((b + d) / e)**2
    k = (pAo - pAe) / (1 - pAe)
    return k

def alpha(annots1, annots2):
    """Implements Krippendorfs alpha agreement score, it is equivalent to kappa"""
    a = vilain_num(annots1, annots2)
    b = vilain_denom(annots2) - a
    c = vilain_denom(annots1) - a
    d = total_possible_links(annots1, annots2) - a - b - c
    e = float(a + b + c + d)

    pDo = (b / e) + (c / e)
    pDe = (((a + c) / e) * ((b + d) / e) + ((a + c) / e) * ((b + d) / e))
    alpha = 1 - (pDo / pDe)
    return alpha

def f(recall, precision):
    """Computes the f-measure score"""
    try:
        return 2 * (float((precision * recall)) / (precision + recall))
    except ZeroDivisionError:
        return 0.0

if __name__ == "__main__":
    #docs = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13")
    docs = ("0", "1", "2", "3", "4")
    doc1 = "/home/ngilbert/xspace/annotations/promed/tuning/nathan/"
    doc2 = "/home/ngilbert/xspace/annotations/promed/tuning/ruihong/"
    #doc1 = "/home/ngilbert/xspace/annotations/muc4/nathan/"
    #doc2 = "/home/ngilbert/xspace/annotations/muc4/ruihong/"

    for d in docs:
        annots1 = reconcile.parseGoldAnnots(doc1 + d)
        annots2 = reconcile.parseGoldAnnots(doc2 + d)
        muc_score = vilain(annots1, annots2)
        k = kappa(annots1, annots2)
        a = alpha(annots1, annots2)
        print "Doc %s\nkappa: %0.6f" % (d, k)
        print "alpha: %0.2f" % (a)
        print "MUCScore: (P/R/F) ",
        print "(%0.2f/%0.2f/%0.2f)" %muc_score
