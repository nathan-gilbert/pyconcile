#!/usr/bin/python
# File Name : reconcile.py
# Purpose : Python script for interface with Reconcile annots files.
# Creation Date : 10-01-2010
# Last Modified : Wed 12 Feb 2014 01:59:56 PM MST
# Created By : Nathan Gilbert
#
import sys
import re
import glob
import string
from collections import defaultdict

import nltk
from nltk.corpus import verbnet

import data
import utils
import feature_utils
from annotation import Annotation
from annotation_set import AnnotationSet

def parseGoldAnnots(dataDir, sundance=False):
    goldFile = glob.glob(dataDir + "/annotations/*_annots")

    for fn in goldFile:
        if fn.endswith("wn_specificity_annots"):
            goldFile.remove(fn)

    if dataDir+"/annotations/coref_annots" in goldFile:
        annotFile = open(goldFile[goldFile.index(dataDir+"/annotations/coref_annots")], 'r')
    else:
        annotFile = open(goldFile[0], 'r')

    rawTxt = open(dataDir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    #pos = getPOS(dataDir)

    span = re.compile('(\d+),(\d+)')
    ID = re.compile('\s+ID=\"([^"]*)\"')
    COREF_ID = re.compile('CorefID=\"([^"]*)\"')
    REF = re.compile('REF=\"([^"]*)\"')
    TYPE = re.compile('TYPE=\"([^"]*)\"')
    CATEGORY = re.compile('CATEGORY=\"([^"]*)\"')
    MIN = re.compile('MIN=\"([^"]*)\"')
    MIN2 = re.compile('Min=\"([^"]*)\"')
    SINGLETON = re.compile('SINGLETON=\"([^"]*)\"')
    ROLE = re.compile('ROLE=\"([^"]*)\"')
    SEMANTIC = re.compile('SEMANTIC=\"([^"]*)\"')
    HEADS = re.compile('HEAD_START=\"([^"]*)\"')
    HEADE = re.compile('HEAD_END=\"([^"]*)\"')
    LETTER = re.compile('LETTER=\"([^"]*)\"')
    UPPERCASE = re.compile('[A-Z]')

    annotations = AnnotationSet("gold_nps")
    gs_nps = None

    for line in annotFile:
        line = line.strip()
        if line.startswith("#") or line.find("COREF") < 0:
            continue

        tokens = line.split("\t")
        attr = {}
        npID = ""
        start = ""
        end = ""

        match1 = span.search(line)
        match2 = ID.search(line)
        if match1 or match2:
            if match1:
                start = int(match1.group(1))
                end = int(match1.group(2))
                text = allLines[start:end]
                attr["TEXT"] = text
                attr["TEXT_CLEAN"] = utils.textClean(text)
                match1 = False
            if match2:
                npID = match2.group(1)
                attr["ID"] = npID
                match2 = False

        #get the POS
        #np_pos = pos.getOverlapping(Annotation(start, end, -1, {},""))
        #attr["POS"] = np_pos.getList()

        match = REF.search(line)
        if match:
            tmp = int(match.group(1))
            if tmp != npID:
                attr["REF"] = tmp

        #for testing scoring algorithms
        match = LETTER.search(line)
        if match:
            tmp = match.group(1)
            if tmp != "":
                attr["LETTER"] = tmp

        match = ROLE.search(line)
        if match:
            attr["ROLE"] = match.group(1)

        match = CATEGORY.search(line)
        if match:
            tmp = match.group(1)
            if tmp.startswith("PRO"):
                attr["is_pronoun"] = True
                attr["is_proper"] = False
                attr["is_nominal"] = False
            elif tmp.startswith("NOM"):
                attr["is_proper"] = False
                attr["is_pronoun"] = False
                attr["is_nominal"] = True
            elif tmp.startswith("NAM"):
                attr["is_proper"] = True
                attr["is_pronoun"] = False
                attr["is_nominal"] = False
            else:
                attr["is_proper"] = False
                attr["is_pronoun"] = False
                attr["is_nominal"] = False
            attr["GOLD_TYPE"] = tmp
        else:
            #see how well we can do this automagically...
            if (attr["TEXT"].lower() in data.ALL_PRONOUNS):
                attr["is_pronoun"] = True
                attr["is_proper"] = False
                attr["is_nominal"] = False
            elif (attr["TEXT"].islower()) and \
                    (attr["TEXT"].lower() not in data.ALL_PRONOUNS):
                attr["is_proper"] = False
                attr["is_pronoun"] = False
                attr["is_nominal"] = True
            elif UPPERCASE.search(attr["TEXT"]):
                attr["is_proper"] = True
                attr["is_pronoun"] = False
                attr["is_nominal"] = False
            else:
                attr["is_proper"] = False
                attr["is_pronoun"] = False
                attr["is_nominal"] = False
            attr["GOLD_TYPE"] = "UNKNOWN"

        #if attr["DATE"] != "NONE":
        #    attr["is_date"] = True
        #else:
        #    attr["is_date"] = False

        match = MIN.search(line)
        if match:
            tmp = match.group(1)
            attr["MIN"] = tmp.replace("\n", " ")
        else:
            match = MIN2.search(line)
            if match:
                tmp = match.group(1)
                attr["MIN"] = tmp.replace("\n", " ")

        match = COREF_ID.search(line)
        if match:
            tmp = int(match.group(1))
            attr["COREF_ID"] = tmp
        else:
            #we have a problem here...
            if gs_nps is None:
                #read in the gsNPs file and grab the CorefID
                gs_nps = getGSNPs(dataDir)
                attr["COREF_ID"] = \
                gs_nps.getAnnotByID(npID).getATTR("COREF_ID")
            else:
                attr["COREF_ID"] = \
                gs_nps.getAnnotByID(npID).getATTR("COREF_ID")

        match = SEMANTIC.search(line)
        if match:
            tmp = match.group(1)
            if tmp.find(":") > -1:
                attr["GOLD_SEMANTIC"] = tmp.split(":")[0]
                attr["GOLD_SEMANTIC2"] = tmp.split(":")[1]
            else:
                attr["GOLD_SEMANTIC"] = tmp

        match = SINGLETON.search(line)
        if match:
            tmp = match.group(1)
            if tmp == "TRUE":
                attr["GOLD_SINGLETON"] = True
            else:
                attr["GOLD_SINGLETON"] = False

        match = HEADS.search(line)
        if match:
            head_start = int(match.group(1))
            attr["HEAD_START"] = head_start
        else:
            head_start = -1

        match = HEADE.search(line)
        if match:
            head_end = int(match.group(1))
            attr["HEAD_END"] = head_end
        else:
            head_end = -1

        #should only work for ACE docs
        if attr.get("HEAD_START", -1) > -1 and attr.get("HEAD_END", -1) > -1:
            head = allLines[head_start:head_end]
            attr["HEAD"] = head

        #get the head if we were given a MIN tag
        if (attr.get("MIN","") != "") and (attr.get("MIN","") != attr["TEXT"]):
            #if we have a "MIN" than let's use it as the head
            attr["HEAD_TEXT"] = attr["MIN"].replace("\n", " ")
        elif (head_start > -1) and (head_end > -1):
            #if we could find a head span, then use it for the head_text
            attr["HEAD_TEXT"] = allLines[head_start:head_end]
        else:
            #set the head_text to None so we can try to change it later
            attr["HEAD_TEXT"] = None

        attr["MATCHED"] = -1
        a = Annotation(start, end, npID, attr, text)
        annotations.add(a)
    annotFile.close()
    rawTxt.close()

    if sundance:
        addSundanceProps(dataDir, annotations)

    return annotations

def getNPType(annot):
    """ Returns the NP type"""
    if annot.getATTR("is_pronoun"):
        return "PRO"
    elif annot.getATTR("is_proper"):
        return "PRP"
    elif annot.getATTR("is_nominal"):
        return "NOM"
    else:
        return "UNK"
    return "UNK"

def getGoldChains(dataDir, sundance=False):
    """returns a dictionary of gold chains. chain_id -> [list of annots]"""

    gold_annots = parseGoldAnnots(dataDir, sundance).getList()
    chains = defaultdict(list)
    for a in gold_annots:
        coref_id = a.getATTR("COREF_ID")
        chains[coref_id].append(a)

    final_chains = defaultdict(list)
    for c in chains.keys():
        final_chains[c] = sortAnnotsBySpans(chains[c])
    return final_chains

def getGSNPs(dataDir):
    """Reads in the gsNPs file, holds all CorefIDs."""

    SPAN = re.compile('(\d+),(\d+)')
    ID = re.compile('\s+ID=\"([^"]*)\"')
    NUM = re.compile('\s+NO=\"([^"]*)\"')
    COREF_ID = re.compile('CorefID=\"([^"]*)\"')
    MATCHED = re.compile('matched_ce=\"([^"]*)\"')

    gs_nps = AnnotationSet("gsNps")
    gsFile = open(dataDir + "/annotations/gsNPs", 'r')
    for line in gsFile:
        line = line.strip()
        attr = {}

        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))

        match = ID.search(line)
        if match:
            a_id = int(match.group(1))

        match = COREF_ID.search(line)
        if match:
            c_id = int(match.group(1))
            attr["COREF_ID"] = c_id

        match = MATCHED.search(line)
        if match:
            ce = int(match.group(1))
            attr["MATCHED"] = ce

        match = NUM.search(line)
        if match:
            number = int(match.group(1))
            attr["NO"] = number

        a = Annotation(start, end, a_id, attr, "")
        gs_nps.add(a)
    gsFile.close()
    return gs_nps

def getFeatures(datadir, featurefile):
    return feature_utils.getFeatures(datadir, featurefile)

def getPairFeatures(antecedent, anaphor, features):
    return feature_utils.getPairFeatures(antecedent, anaphro, features)

def getStanfordDep(datadir):
    GOV_SPAN = re.compile('GOV_SPAN=\"([^"]*)\"')
    GOV = re.compile('GOV=\"([^"]*)\"')
    DEP_SPAN = re.compile('DEP_SPAN=\"([^"]*)\"')
    DEP = re.compile('DEP=\"([^"]*)\"')

    deps = AnnotationSet("stanford dep")
    with open(datadir+"/annotations/stanford_dep", 'r') as depFile:
        for line in depFile:
            line=line.strip()
            tokens = line.split()
            num = int(tokens[0].strip())
            attr = {}

            relation = tokens[1].strip()
            attr["RELATION"] = relation

            match = GOV.search(line)
            if match:
                gov = match.group(1).strip()
                attr["GOV"] = gov

            match = GOV_SPAN.search(line)
            if match:
                gov_span = match.group(1).strip()
                gov_start = int(gov_span.split(",")[0])
                gov_end = int(gov_span.split(",")[1])
                attr["GOV_SPAN"] = gov_span

            match = DEP_SPAN.search(line)
            if match:
                dep_span = match.group(1).strip()
                dep_start = int(dep_span.split(",")[0])
                dep_end = int(dep_span.split(",")[1])
                attr["DEP_SPAN"] = dep_span

            match = DEP.search(line)
            if match:
                dep = match.group(1).strip()
                attr["DEP"] = dep

            start = gov_start if (gov_start <= dep_start) else dep_start
            end = gov_end if (gov_end >= dep_end) else dep_end

            a = Annotation(start,end,num,attr,"")
            deps.add(a)
    return deps

def getPreviousAntecedent(anaphor, gold_chains):
    prev = Annotation(-1, -1, -1, {}, "")
    for chain in gold_chains.keys():
        for markable in gold_chains[chain]:
            if (markable.getStart() == anaphor.getStart()) and (markable.getEnd() == anaphor.getEnd()):
                return prev
            prev = markable
    return prev

def getPreviousProperAntecedent(anaphor, gold_chains):
    prev = None
    for chain in gold_chains.keys():
        for markable in gold_chains[chain]:
            if (markable.getStart() == anaphor.getStart()) and (markable.getEnd() == anaphor.getEnd()):
                return prev
            if markable.getATTR("is_proper"):
                prev = markable
    return prev

def getPreContexts(datadir):
    pre_contexts = AnnotationSet("pre_contexts")
    contextFile = open(datadir + "/annotations/precontexts")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    i = 0
    for line in contextFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        a = Annotation(start, end, i, {"PRE_CONTEXT": tokens[3]}, lines[start:end])
        pre_contexts.add(a)
        i += 1
    return pre_contexts

def getPostContexts(datadir):
    post_contexts = AnnotationSet("post_contexts")
    contextFile = open(datadir + "/annotations/postcontexts")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    i = 0
    for line in contextFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        a = Annotation(start, end, i, {"POST_CONTEXT": tokens[3]}, lines[start:end])
        post_contexts.add(a)
        i += 1
    return post_contexts

def sortAnnotsBySpans(pairs):
    s = sorted(pairs, key=lambda x : x.getStart())
    return sorted(s, key=lambda x : x.getEnd())

def sortBySpans(spans):
    s = sorted(spans, key=lambda x : int(x.split(":")[1]))
    return sorted(s, key=lambda x : int(x.split(":")[0]))

def fixREFNumbers(clusters):
    """Takes a dictonary of clusters and re-arranges the REF/ID tags to be in order."""
    for key in clusters.keys():
        prevREF = -1
        for mention in clusters[key]:
            if mention.getREF() != -1:
                mention.setREF(prevREF)
            prevREF = mention.getID()

def chainAnnots(annots):
    chains = []
    #while len(annots) > 0:
    for a in annots:
        cur = a
        if cur.getREF() == -1:
            chains.append([cur])
        else:
            found = False
            for entity in chains:
                for instance in entity:
                    if cur.getREF() == instance.getID():
                        entity.append(cur)
                        found = True
            #if not found:
            #    annots.append(cur)
    return chains

def orderedChains(chains):
    """Order chains by bytespan (where they appear in the document"""
    newChains = []
    for c in chains:
        c.sort()
        newChains.append(c)
    return newChains

def getSundanceClauses(datadir):
    clauseFile = open(datadir + "/annotations/sclause")
    span = re.compile('(\d+),(\d+)')
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    clauses = AnnotationSet("sundance_clauses")
    ID = 0
    for line in clauseFile:
        line = line.strip()
        attr = {}
        match = span.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end].replace("\n", " ")
            attr["TEXT"] = text
        if start == -1 or start > end:
            continue
        clauses.add(Annotation(start, end, ID, attr, text))
        ID+=1
    return clauses

def getMatchedSundanceNEs(datadir):
    SPAN = re.compile('(\d+),(\d+)')
    nes = AnnotationSet("sundance nes")
    try:
        neFile = open(datadir+"/annotations/sne_matched", 'r')
    except:
        return nes

    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    i=0
    for line in neFile:
        line=line.strip()
        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
        tokens = line.split()
        #grab all the semantic classes, not just the first one
        #which means that this is now a list instead of a string
        ne_classes = map(lambda x : x.strip(), tokens[2].split(","))
        a = Annotation(start, end, i, {"SUN_NE" : ne_classes}, text)
        nes.add(a)
    return nes

def getSundanceNEs(datadir):
    """returns an annotation set of sundances NE"""
    SPAN = re.compile('(\d+),(\d+)')
    nes = AnnotationSet("sundance nes")
    try:
        neFile = open(datadir+"/annotations/sne", 'r')
    except:
        return nes

    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    i=0
    for line in neFile:
        line=line.strip()
        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
        tokens = line.split()
        #grab all the semantic classes, not just the first one
        #which means that this is now a list instead of a string
        ne_class = tokens[3:]
        a = Annotation(start, end, i, {"SUN_NE" : ne_class}, text)
        nes.add(a)
    return nes

def getSundanceNPs(datadir):
    """return an annotation set of the Sundance created nps"""
    SPAN = re.compile('(\d+),(\d+)')
    MORPH = re.compile('MORPH=\"([^"]*)\"')
    ROLE = re.compile('ROLE=\"([^"]*)\"')
    SEM = re.compile('SEM=\"([^"]*)\"')

    nps = AnnotationSet("sundance nps")
    sundance_file = open(datadir + "/annotations/snps", 'r')
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()

    i=0
    for line in sundance_file:
        line = line.strip()
        attr = {}

        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]

        match = MORPH.search(line)
        if match:
            attr["MORPH"] = match.group(1)

        match = ROLE.search(line)
        if match:
            attr["ROLE"] = match.group(1)

        match = SEM.search(line)
        if match:
            attr["SEM"] = match.group(1)

        nps.add(Annotation(start, end, i, attr, text))
        i += 1
    return nps

def addSundanceProps(datadir, nps):
    """Takes a set of nps_annots and adds in Sundance ne/nps info"""
    SPAN = re.compile('(\d+),(\d+)')
    SEM = re.compile('.*SEM=\"([^"]*)\".*')
    ROLE = re.compile('.*ROLE=\"([^"]*)\".*')
    MORPH = re.compile('.*MORPH=\"([^"]*)\".*')

    try:
        #snpsFile = open(datadir + "/annotations/snps", 'r')
        sneFile = open(datadir + "/annotations/sne", 'r') #right now, more nes
                                                          #are collected in this file than in the nps file.
                                                          #ng 03/04/2013
    except:
        return

    #cycling over all sundance nes
    for line in sneFile:
        line = line.strip()
        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            tokens = line.split()
            if len(tokens) > 3:
                semantics = tokens[3:]
                #find the noun phrases that correspond to this ne
                for np in nps:
                    #method 1: use Reconcile's head demarcations [not so good]
                    head_start = int(np.getATTR("HEAD_START"))
                    head_end = int(np.getATTR("HEAD_END"))
                    if (start == head_start and end == head_end):
                        if np.hasProp("SUN_SEMANTIC") and np.getATTR("SUN_SEMANTIC") is not None:
                            for sem in semantics:
                                if sem not in np.attr["SUN_SEMANTIC"]:
                                    np.attr["SUN_SEMANTIC"].append(sem.replace("-","_"))
                        else:
                            np.setProp("SUN_SEMANTIC", [])
                            for sem in semantics:
                                np.attr["SUN_SEMANTIC"].append(sem.replace("-","_"))
                        break

                    #method 2: attempt to determine the head on my own
                    #TODO not working yet...
                    #if (start >= np.getStart()) and (end <= np.getEnd()):
                    #    sem_start = start - np.getStart()
                    #    sem_end = end
                        #this is causing some bad semantic classes to be
                        #assigned, really need to grab the semantic class of
                        #the head and nothing more.
                    #    if not utils.spanInPrep(sem_start, np.getText()) \
                    #            and not utils.spanInAppositive(sem_start, np.getText()) \
                    #            and utils.spanInHead(sem_start, sem_end, np.getText()):
                    #        if np.hasProp("SUN_SEMANTIC") and np.getATTR("SUN_SEMANTIC") is not None:
                    #            for sem in semantics:
                    #                if sem not in np.attr["SUN_SEMANTIC"]:
                    #                    np.attr["SUN_SEMANTIC"].append(sem)
                    #        else:
                    #            np.setProp("SUN_SEMANTIC", semantics)
                    #        break

    #for line in snpsFile:
    #    line = line.strip()
    #    match = SPAN.search(line)
    #    if match:
    #        start = int(match.group(1))
    #        end = int(match.group(2))

        #match = SEM.search(line)
        #if match:
        #    semantics = match.group(1).split("|")
        #    if "ENTITY" in semantics and "UNKNOWN" in semantics:
        #        semantics = None
        #    for np in nps:
        #        if (start >= np.getStart()) and (end <= np.getEnd()):
        #            sem_start = start - np.getStart()
        #            if not utils.spanInPrep(sem_start, np.getText())\
        #                and not utils.spanInAppositive(sem_start,np.getText()):
        #                np.setProp("SUN_SEMANTIC", semantics)
        #                break
        #else:
        #    semantics = None

    #    match = ROLE.search(line)
    #    if match:
    #        srole = match.group(1)
    #        nps.addPropBySpan(start, end, "SUN_ROLE", srole)

    #    match = MORPH.search(line)
    #    if match:
    #        smorph = match.group(1)
    #        nps.addPropBySpan(start, end, "SUN_MORPH", smorph)
    #snpsFile.close()
    sneFile.close()

def getStanfordNPs(datadir):
    """
    returns an annotation set of the NPs that the stanford parser has created.
    """
    TEXT = re.compile('.*Text=\"([^"]*)\".*')
    POS =  re.compile('.*\tPOS=\"([^"]*)\".*')
    HEAD = re.compile('.*Head=\"([^"]*)\".*')
    HEADPOS = re.compile('.*HeadPOS=\"([^"]*)\".*')
    HEAD_START = re.compile('.*HEAD_START=\"([^"]*)\".*')
    HEAD_END = re.compile('.*HEAD_END=\"([^"]*)\".*')
    with open(datadir + "/raw.txt", 'r') as txtFile:
        allLines = ''.join(txtFile.readlines())

    stanford_nps = AnnotationSet("stanford nps")
    with open(datadir + "/annotations/stanford_nps", 'r') as npFile:
        num = 0
        for line in npFile:
            attr = {}
            tokens = line.split()
            start = int(tokens[1].split(",")[0])
            end = int(tokens[1].split(",")[1])

            match = TEXT.search(line)
            if match:
                text = match.group(1)
                attr["Text"] = text

            match = POS.search(line)
            if match:
                pos = match.group(1).replace("[", "").replace("]","").strip()
                pos_tuples = map(lambda x : nltk.tag.str2tuple(x),
                        map(lambda x : x.strip(), pos.split(", ")))
                attr["POS"] = pos_tuples

            match = HEADPOS.search(line)
            if match:
                head_pos = match.group(1).replace("[","").replace("]","").strip()
                head_pos_tuples = map(lambda x : nltk.tag.str2tuple(x),
                        map(lambda x : x.strip(), head_pos.split(",")))
                attr["HEAD_POS"] = head_pos_tuples

            match = HEAD_START.search(line)
            if match:
                head_start = int(match.group(1))
                attr["HEAD_START"] = head_start

            match = HEAD_END.search(line)
            if match:
                head_end = int(match.group(1))
                attr["HEAD_END"] = head_end

            match = HEAD.search(line)
            if match:
                head = match.group(1).strip()
                if head == "'s":
                    new_head = ""
                    i = 0
                    propers = []

                    #NOTE building the proper name from the beginning, this may
                    #cause problems if there is a huge NP with multiple
                    #possessives
                    for tup in pos_tuples:
                        if tup[1].strip() in ("NNP", "NNPS"):
                            propers.append(tup)
                        elif tup[0].strip() in ("'s"):
                            pass
                        else:
                            propers = []

                        if tup[0] == "'s":
                            if pos_tuples[i-1][1].strip() in ("NN" or "NNS"):
                                #if a common noun, try to get the entire string
                                new_head = pos_tuples[i-1][0].strip()
                                attr["HEAD_POS"] = [pos_tuples[i-1]]
                                attr["HEAD_START"] = text.find(new_head) + start
                                attr["HEAD_END"] = attr["HEAD_START"] + len(new_head)
                            elif pos_tuples[i-1][1].strip() in ("NNP" or "NNPS"):
                                #if a proper noun, try to get the entire string
                                new_head = ' '.join(map(lambda x : x[0],
                                    propers))
                                attr["HEAD_POS"] = propers
                                attr["HEAD_START"] = text.find(new_head) + start
                                attr["HEAD_END"] = attr["HEAD_START"] + len(new_head)
                            else:
                                #just give it the last token otherwise
                                new_head = pos_tuples[i-1][0].strip()
                            break

                        i+=1
                    attr["HEAD"] = new_head.strip()
                elif head in ("%", "="):
                    new_head = ""
                    i = 0
                    for tup in pos_tuples:
                        if (tup[0] == "%") or (tup[0] == "="):
                            new_head = pos_tuples[i-1][0].strip() + tup[0]
                            attr["HEAD_POS"] = [pos_tuples[i-1], pos_tuples[i]]
                            attr["HEAD_START"] = text.find(new_head) + start
                            attr["HEAD_END"] = attr["HEAD_START"] + len(new_head)
                            break
                        i+=1
                    attr["HEAD"] = new_head.strip()
                else:
                    attr["HEAD"] = head

            attr["HEAD"] = attr["HEAD"].replace("$ ", "$").replace("# ", "#")

            if attr["HEAD_POS"][-1][1] in ("NNP", "NNPS"):
                attr["is_proper"] = True
                attr["is_pronoun"] = False
                attr["is_nominal"] = False
            elif attr["HEAD_POS"][-1][1] in ("NN", "NNS"):
                attr["is_nominal"] = True
                attr["is_proper"] = False
                attr["is_pronoun"] = False
            elif attr["HEAD_POS"][-1][1] in ("PRP", "PRP$", "WP", "WP$"):
                attr["is_pronoun"] = True
                attr["is_proper"] = False
                attr["is_nominal"] = False
            else:
                attr["is_proper"] = True
                attr["is_pronoun"] = False
                attr["is_nominal"] = False

            a = Annotation(start, end, num, attr, text)
            stanford_nps.add(a)
            num+=1

    return filterStanfordDuplicates(stanford_nps)
    #return stanford_nps

def filterStanfordDuplicates(nps):
    """
    if the previous noun in the file overlaps with the current noun
    and the head of the previous noun is the last token of the head of
    the current noun, then we have a subsumed noun phrase. we need to
    remove the subsumed np and update the head of the current np to the
    subsumed np's head
    """
    #TODO need to handle conjunctions better. [it would be better to have both
    #sides of the conjunctions with the conjuction maximal NP
    #currently, the head of the conjunction phrase is the first NP's head
    #TODO need to make sure that Proper nouns have their maximal head:
    #currently: Siemens AG => AG
    new_stanford_nps = AnnotationSet("stanford nps")
    prev_np = None
    for np in nps:
        if (prev_np is not None) and np.contains(prev_np):
            #is the head of the previous noun the last token in the current
            #noun?
            if prev_np["HEAD"] == np["HEAD"].split()[-1]:
                #print "{0} contains {1}".format(np.getText(), prev_np.getText())
                np["HEAD"] = prev_np["HEAD"]
                np["HEAD_START"] = prev_np["HEAD_START"]
                np["HEAD_END"] = prev_np["HEAD_END"]
                np["HEAD_POS"] = prev_np["HEAD_POS"]
                new_stanford_nps.removeAnnot(prev_np)
                new_stanford_nps.add(np)
            else:
                new_stanford_nps.add(np)
        else:
            new_stanford_nps.add(np)
        prev_np = np
    new_stanford_nps.fixIDs()
    return new_stanford_nps

def getNPs(datadir):
    """
    @param datadir: the base directory for this data file
    """
    return getNPs_annots(datadir)

def getNPs_annots(datadir):
    """ datadir -> annotation_set """
    #NOTE: changes made to this since *sem 2012
    # 1. instead of reading from the "TEXT" prop for getText() value, pulling
    #    directly from raw text file now.
    nps = getNPs_props(datadir)
    annots = AnnotationSet("nps")
    with open(datadir + "/raw.txt", 'r') as rawTxt:
        allLines = ''.join(rawTxt.readlines())

    for n in nps:
        start = n[0]
        end = n[1]
        props = n[2]
        a = Annotation(start, end, props["NO"], props, allLines[start:end])
        annots.add(a)
    return annots

def getNPs_props(datadir):
    """ Returns a list of nps (not annotations) populated with data from the npProperties file. """

    npProps = open(datadir + "/annotations/npProperties", 'r')
    nps = []
    PRO = re.compile('.*Pronoun=\"([^"]*)\".*')
    PN = re.compile('.*ProperName=\"([^"]*)\".*')
    PNoun = re.compile('.*ProperNoun=\"([^"]*)\".*')
    GEN = re.compile('.*Gender=\"([^"]*)\".*')
    ACRONYM = re.compile('.*ContainsAcronym=\"([^"]*)\".*')
    NUM = re.compile('.* Number=\"([^"]*)\".*')
    QUOTE = re.compile('.*InQuote=\"([^"]*)\".*')
    SEM = re.compile('.*NPSemanticType=\"([^"]*)\".*')
    SUN_SEM = re.compile('.*SundanceSemanticType=\"([^"]*)\".*')
    TEXT = re.compile('.*Text=\"([^"]*)\".*')
    DATE = re.compile('.*DATE=\"([^"]*)\".*')
    YEAR = re.compile('.*(19\d\d).*')
    MOD = re.compile('.*Modifier=\"([^"]*)\".*')
    ROLE = re.compile('.*\sGramRole=\"([^"]*)\".*')
    DEFN = re.compile('.*Definite=\"([^"]*)\".*')
    SYN = re.compile('.*Synsets=\"([^"]*)\".*')
    COREFID = re.compile('.*CorefID=\"([^"]*)\".*')
    HEAD_NOUN = re.compile('.*HeadNoun=\"([^"]*)\".*')
    NO = re.compile('.*NO=\"([^"]*)\".*')
    CONTAINSPN = re.compile('.*ContainsProperName=\"([^"]*)\".*')

    for line in npProps:
        props = {}
        line = line.strip()
        tokens = line.split()

        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])

        match = PRO.match(line)
        if match:
            p = match.group(1)
            props["PRONOUN"] = p
        else:
            props["PRONOUN"] = "NONE"

        match = PN.match(line)
        if match:
            p = match.group(1)
            props["PROPER_NAME"] = p
        else:
            props["PROPER_NAME"] = "NONE"

        match = PNoun.match(line)
        if match:
            p = match.group(1)
            props["PROPER_NOUN"] = p
        else:
            props["PROPER_NOUN"] = "NONE"

        numMatch = NUM.match(line)
        if numMatch:
            num = numMatch.group(1)
            props['NUMBER'] = num
        else:
            props['NUMBER'] = "UNKNOWN"

        match = GEN.match(line)
        if match:
            g = match.group(1)
            props["GENDER"] = g
        else:
            props["GENDER"] = "UNKNOWN"

        match = DEFN.match(line)
        if match:
            d = match.group(1)
            if d == "true":
                props["is_definite"] = True
            else:
                props["is_definite"] = False
        else:
            props["is_definite"] = False

        match = COREFID.match(line)
        if match:
            cid = int(match.group(1))
            props["COREF_ID"] = cid
        else:
            props["COREF_ID"] = -1

        match = ACRONYM.match(line)
        if match:
            d = match.group(1)
            if d == "true":
                props["is_Acronym"] = True
            else:
                props["is_Acronym"] = False
        else:
            props["is_Acronym"] = False

        match = NO.match(line)
        if match:
            no = int(match.group(1))
            props["NO"] = no
        else:
            props["NO"] = -1

        match = DATE.match(line)
        if match:
            d = match.group(1)
            props["DATE"] = d
        else:
            props["DATE"] = "NONE"

        match = MOD.match(line)
        if match:
            mods = match.group(1)
            mods = mods.replace("[", "").replace("]", "").strip()
            props["MODIFIER"] = mods
        else:
            props["MODIFIER"] = ""

        match = SYN.match(line)
        if match:
            sets = match.group(1)
            sets = sets.replace("{", "").split("}")
            synsets = []
            for s in sets:
                tokens = s.split()
                if tokens not in synsets and tokens != []:
                    synsets.append(tokens)
            props["SYNSETS"] = synsets

            if ("date" in synsets) or ("time" in synsets):
                props["DATE"] = "DATE"
        else:
            props["SYNSETS"] = []

        match = SEM.match(line)
        if match:
            s = match.group(1)
            props["SEMANTIC"] = s

            if s == "DATE":
                props["DATE"] = "DATE"
        else:
            props["SEMANTIC"] = "NONE"

        match = SUN_SEM.match(line)
        if match:
            s = match.group(1)
            s = s.replace("[","").replace("]","")
            s_tok = s.split()
            props["SUN_SEMANTIC"] = s_tok

            for tok in s_tok:
                if tok in ("DATE","MONTH","DAY","YEAR"):
                    props["DATE"] = "DATE"
        else:
            props["SUN_SEMANTIC"] = None

        match = TEXT.match(line)
        if match:
            t = match.group(1)
            props["TEXT"] = t
            props["TEXT_LOWER"] = t.lower()
            props["TEXT_CLEAN"] = utils.textClean(t)
            #try:
            #    head = t.split()[-1]
            #    props["HEAD_TEXT"] = t.split()[-1]
            #    props["HEAD_START"] = end - len(head)
            #    props["HEAD_END"] = end
            #except IndexError:
            #    pass

        match = CONTAINSPN.match(line)
        if match:
            pn_span = match.group(1)
            pn_start = int(pn_span.split(",")[0])
            pn_end = int(pn_span.split(",")[1])
            if pn_start == -1 and pn_end == -1:
                props["contains_pn"] = None
            else:
                if pn_start < start:
                    pn_start = 0
                else:
                    pn_start = pn_start - start
                pn_end = pn_end - start
                props["pn_start"] = pn_start
                props["pn_end"]   = pn_end
                props["contains_pn"] = props["TEXT"][pn_start:pn_end] #(pn_start - start, pn_end - start)
        else:
            props["contains_pn"] = None

        match = YEAR.match(props["TEXT"])
        if match and props["DATE"] == "NONE":
            props["DATE"] = "DATE"

        if props["DATE"] != "NONE":
            props["is_date"] = True
        else:
            props["is_date"] = False

        #get indefinite
        t = props["TEXT_LOWER"]
        if t.startswith("a "):
            props["is_indefinite"] = True
        else:
            props["is_indefinite"] = False

        roleMatch = ROLE.match(line)
        if roleMatch:
            g = roleMatch.group(1)
            props["GRAMMAR"] = g
        else:
            props["GRAMMAR"] = "NONE"

        match = HEAD_NOUN.match(line)
        if match:
            span = match.group(1).split(",")
            head_start = int(span[0].strip())
            head_end = int(span[1].strip())
            props["HEAD_START"] = head_start
            props["HEAD_END"] = head_end

        match = QUOTE.match(line)
        if match:
            #q = match.group(1)
            props["in_quote"] = True
        else:
            props["in_quote"] = False

        if props["TEXT_LOWER"] == "it's":
            props["it_is"] = True
        else:
            props["it_is"] = False

        if (props["PRONOUN"] != "NONE") or (props["TEXT_LOWER"] in \
                data.ALL_PRONOUNS):
            props["is_pronoun"] = True
            props["is_proper"] = False
            props["is_nominal"] = False
        elif (props["PRONOUN"] == "NONE") and (props["PROPER_NOUN"] == "false"):
            props["is_nominal"] = True
            props["is_pronoun"] = False
            props["is_proper"] = False
        elif (props["PROPER_NOUN"] == "true"):
            props["is_proper"] = True
            props["is_nominal"] = False
            props["is_pronoun"] = False
        else:
            props["is_nominal"] = False
            props["is_proper"] = False
            props["is_pronoun"] = False

        nps.append((start, end, props))
    npProps.close()
    return nps

def getAnnots(datadir, filetype):
    try:
        duncanFile = open(datadir + "/annotations/" + filetype, 'r')
    except:
        sys.stderr.write("Error: %s not found in %s" % (filetype, datadir))
        return []

    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())

    span = re.compile('(\d+),(\d+)')
    ID = re.compile('.*ID=\"([^"]*)\".*')
    REF = re.compile('.*REF=\"([^"]*)\".*')
    MIN = re.compile('.*MIN=\"([^"]*)\".*')

    annotations = AnnotationSet(filetype)
    for line in duncanFile:
        line = line.strip()
        if line.startswith("#"):
            continue

        tokens = line.split("\t")
        attr = {}
        npID = ""
        start = ""
        end = ""

        matchType = tokens[-1] if len(tokens) == 7 else ""

        #throw away first element, just reconcile internal ID
        for t in tokens[1:]:
            match1 = span.match(t)
            match2 = ID.match(t)
            if match1 or match2:
                if match1:
                    start = match1.group(1)
                    end = match1.group(2)
                    text = allLines[int(start):int(end)].replace("\n", " ")
                    match1 = False
                if match2:
                    npID = match2.group(1)
                    match2 = False

            match = REF.match(t)
            if match:
                tmp = match.group(1)
                attr["REF"] = tmp

            match = MIN.match(t)
            if match:
                tmp = match.group(1)
                attr["MIN"] = tmp.replace("\n", " ")
            else:
                attr["MIN"] = text

        if matchType != "":
            attr["TYPE"] = matchType

        if (start != "") and (end != "") and (npID != ""):
            a = Annotation(start, end, npID, attr, text)
            annotations.add(a)
    duncanFile.close()
    return annotations

def getPairs(datadir, filetype):
    annotations = getAnnots(datadir, filetype)
    #make pairs
    pairs = []
    for a in annotations:
        ref = int(a.attr.get("REF", -1))
        if ref != -1:
            for b in annotations:
                if ref == b.getID():
                    pairs.append((b, a))
    return pairs

def getGenericAnnots(datadir, aname):
    """Assumes:
        NUM\tSPAN\tPROP1=X\tPROP2=Y...
    """
    annots = AnnotationSet("annotations")
    inFile = open(datadir + "/annotations/" + aname, 'r')
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    rawTxt.close()

    for line in inFile:
        if line.startswith("#"):
            continue
        line = line.strip()
        tokens = line.split()
        ID = int(tokens[0])
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        text = lines[start:end].replace("\n", " ")
        attr = {}
        datatype = tokens[2]
        for t in tokens[3:]:
            prop = t.split("=")[0]
            value = t.split("=")[1].replace("\"", "")
            attr[prop] = value
        annots.add(Annotation(start, end, ID, attr, text))
    return annots

def getCategories(datadir):
    """Returns an AnnotationSet"""
    return getGenericAnnots(datadir, "cats")

def getResponseNPs(datadir, outputfile):
    """returns an annotation set of response nps."""
    responseFile = open(datadir + outputfile + "/coref_output")
    SPAN = re.compile('\s(\d+),(\d+)\s')
    COREF = re.compile('CorefID=\"([^"]*)\"')
    NO = re.compile('NO=\"([^"]*)\"')
    r_nps = AnnotationSet("responses")
    for line in responseFile:
        line = line.strip()
        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))

        match = COREF.search(line)
        if match:
            corefID = int(match.group(1))

        match = NO.search(line)
        if match:
            num = int(match.group(1))

        attr = {"COREF_ID":corefID, "NO":num}
        a = Annotation(start, end, num, attr, "")
        r_nps.add(a)
    return r_nps


def getResponseChains(datadir, outputfile):
    """returns a dictionary of response chains. chain_id -> [list of annots]"""
    responseFile = open(datadir + outputfile + "/coref_output")
    nps = getNPs_annots(datadir)
    #addSundanceProps(datadir, nps)

    SPAN = re.compile('.*\s(\d+),(\d+)\s.*')
    COREF = re.compile('.*CorefID=\"([^"]*)\".*')

    clusters = defaultdict(list)
    for line in responseFile:
        line = line.strip()
        match = SPAN.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))

        match = COREF.search(line)
        if match:
            corefID = int(match.group(1))

        np = nps.getAnnotBySpan(start, end)

        if np.getStart() != -1 and np.getEnd() != -1:
            clusters[corefID].append(np)
        else:
            print "NULL annot"

    final_chains = defaultdict(list)
    for c in clusters.keys():
        final_chains[c] = sortAnnotsBySpans(clusters[c])
    return final_chains

def getReconcileResponses(datadir, outputfile):
    """Duplicating what is going on above in getResponseChains for no *good*
    reason"""
    responseFile = open(datadir + outputfile + "/coref_output")
    span = re.compile('.*\s(\d+),(\d+)\s.*')
    COREF = re.compile('.*CorefID=\"([^"]*)\".*')
    clusters = defaultdict(list)
    nps = getNPs_annots(datadir)
    for line in responseFile:
        line = line.strip()
        match = span.match(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            annot = nps.getAnnotBySpan(start, end)
        match = COREF.match(line)
        if match:
            corefID = match.group(1)
        clusters[corefID].append(annot)
    return clusters

def getAllResponsePairs(datadir, predictions):
    """Returns tuple(antecedent, anaphor, threshold) annotations"""
    responseFile = open(datadir + predictions + "/predictions")
    triple = re.compile('^(\d+),(\d+),(\d+)\s.*')
    nps = getNPs_annots(datadir)
    pairs = []
    for line in responseFile:
        line = line.strip()
        tokens = line.split()
        match = triple.match(line)
        if match:
            antecedent = nps.getAnnotByID(int(match.group(2)))
            anaphor = nps.getAnnotByID(int(match.group(3)))
        pairs.append((antecedent, anaphor, float(tokens[1])))
    return pairs

def getMentionDistancePronounPairs(datadir, predictions):
    lines = []
    with open(datadir + "/" + predictions + "/pronoun.predictions") as fauxFile:
        lines.extend(filter(lambda x : not x.startswith("#"), fauxFile.readlines()))

    nps = getNPs_annots(datadir)
    pairs = []
    for line in lines:
        tokens = line.split("\t")
        ant_start = int(tokens[0].split(",")[0])
        ant_end = int(tokens[0].split(",")[1])
        ana_start = int(tokens[1].split(",")[0])
        ana_end = int(tokens[1].split(",")[1])
        antecedent = nps.getAnnotBySpan(ant_start, ant_end)
        anaphor = nps.getAnnotBySpan(ana_start, ana_end)
        pairs.append((antecedent, anaphor, 1.0))
    return pairs

def getFauxPairs(datadir, predictions):
    lines = []
    with open(datadir + "/" + predictions + "/faux.predictions") as fauxFile:
        lines.extend(filter(lambda x : not x.startswith("#"), fauxFile.readlines()))

    nps = getNPs_annots(datadir)
    pairs = []
    for line in lines:
        tokens = line.split("\t")
        ant_start = int(tokens[0].split(",")[0])
        ant_end = int(tokens[0].split(",")[1])

        ana_start = int(tokens[1].split(",")[0])
        ana_end = int(tokens[1].split(",")[1])

        antecedent = nps.getAnnotBySpan(ant_start, ant_end)
        anaphor = nps.getAnnotBySpan(ana_start, ana_end)

        pairs.append((antecedent, anaphor, 1.0))
    return pairs

def getResponsePairs(datadir, predictions, threshold=1.0):
    """Returns tuple(antecedent, anaphor, threshold) annotations"""
    responseFile = open(datadir + "/" + predictions + "/predictions")
    triple = re.compile('^(\d+),(\d+),(\d+)\s.*')
    nps = getNPs_annots(datadir)
    pairs = []
    for line in responseFile:
        line = line.strip()
        tokens = line.split()
        if float(tokens[1]) >= threshold:
            match = triple.match(line)
            if match:
                antecedent = nps.getAnnotByID(int(match.group(2)))
                anaphor = nps.getAnnotByID(int(match.group(3)))
            pairs.append((antecedent, anaphor, float(tokens[1])))
    return pairs

def getWNLabels(datadir):
    span = re.compile('(\d+),(\d+)')
    sem = re.compile('Semantic=\"([^"]*)\"')
    spec = re.compile('Specificity=\"([^"]*)\"')
    text = re.compile('Text=\"([^"]*)\"')
    head = re.compile('Head=\"([^"]*)\"')

    labels = AnnotationSet("wn_labels")
    with open(datadir+"/annotations/wn_specificity_annots", 'r') as wn_labels:
        i = 0
        for line in wn_labels:
            attr = {}
            line = line.strip()
            match = span.search(line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))

            match = sem.search(line)
            if match:
                attr["Semantic"] = match.group(1)

            match = spec.search(line)
            if match:
                attr["Specificity"] = match.group(1)

            match = text.search(line)
            if match:
                attr["Text"] = match.group(1)
            else:
                attr["Text"] = ""

            match = head.search(line)
            if match:
                attr["Head"] = match.group(1)

            labels.add(Annotation(start, end, i, attr, attr["Text"]))
            i+=1
    return labels

def getResponsePairs2(datadir, predictions, threshold=1.0):
    responseFile = open(datadir + predictions + "/predictions")
    triple = re.compile('^(\d+),(\d+),(\d+)\s.*')
    nps = getNPs_annots(datadir)
    pairs = []
    for line in responseFile:
        line = line.strip()
        tokens = line.split()
        if float(tokens[1]) >= threshold:
            match = triple.match(line)
            if match:
                d = int(match.group(1))
                antecedent = int(match.group(2))
                anaphor = int(match.group(3))
                pairs.append((d, antecedent, anaphor, float(tokens[1])))
    return pairs

def labelCorrectPairs(gold_chains, response_pairs):
    """Returns a set of pairs that are annotated according to the
    gold_chains"""

    #for key in gold_chains.keys():
    #    print key
    #    for mention in gold_chains[key]:
    #        print mention.pprint()

    annotated_pairs = []
    for p in response_pairs:
        antecedent = p[0]
        anaphor = p[1]

        ant_chain = -1
        ana_chain = -2

        for key in gold_chains.keys():
            chain = gold_chains[key]
            for annot in chain:
                if (antecedent == annot):
                    ant_chain = key

                if (anaphor == annot):
                    ana_chain = key

        if (ana_chain == ant_chain):
            annotated_pairs.append((antecedent, anaphor, True))
        else:
            annotated_pairs.append((antecedent, anaphor, False))
            #print "%s (%d) <- %s (%d)" % (antecedent.pprint(), ant_chain,
            #        anaphor.pprint(), ana_chain)
    return annotated_pairs

def isCorrectPair(gold_chains, pair):
    antecedent = pair[0]
    anaphor = pair[1]
    ant_chain = -1
    ana_chain = -2
    for key in gold_chains.keys():
        chain = gold_chains[key]
        for annot in chain:
            if (antecedent == annot):
                ant_chain = key

            if (anaphor == annot):
                ana_chain = key
    if (ana_chain == ant_chain):
        return True
    else:
        return False
    return False

def getParagraphs(datadir):
    parFile = open(datadir + "/annotations/par")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    pars = AnnotationSet("paragraphs")
    i = 0
    for line in parFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        a = Annotation(start, end, i, {"NUM":i}, lines[start:end])
        pars.add(a)
        i += 1
    return pars

def getFauxPronouns(datadir):
    common_nouns = AnnotationSet("faux_pronouns")
    nps = getNPs(datadir)
    with open(datadir + "/raw.txt", 'r') as rawTxt:
        allLines = ''.join(rawTxt.readlines())

    with open(datadir+"/annotations/faux_pronouns", 'r') as inFile:
        i = 0
        for line in inFile:
            if line.startswith("#"): continue
            line=line.strip()
            tokens = line.split()
            span = tokens[1]
            start = int(span.split(",")[0].strip())
            end = int(span.split(",")[1].strip())

            annot = nps.getAnnotBySpan(start, end)
            if annot is None:
                #create a new one
                text = allLines[start:end]
                props = {"Text" : text, ID : i}
                annot = Annotation(start, end, props["ID"], props, text)
                i+=1
            common_nouns.add(annot)
    common_nouns.fixIDs()
    return common_nouns

def getHeidelTime(datadir):
    """
    Returns an annotation set containing the heideltime annotations.
    """
    TYPE = re.compile('type=\"([^"]*)\"')
    VALUE = re.compile('value=\"([^"]*)\"')
    TID = re.compile('tid=\"([^"]*)\"')
    timeFile = open(datadir + "/annotations/time")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    times = AnnotationSet("heideltime")
    i = 0
    for line in timeFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])

        match = TYPE.search(line)
        if match:
            t = match.group(1)
        match = VALUE.search(line)
        if match:
            v = match.group(1)
        match = TID.search(line)
        if match:
            tid = match.group(1)

        a = Annotation(start, end, i, {"TID": tid, "VALUE":v, "TYPE":t}, lines[start:end])
        times.add(a)
        i += 1
    return times

def getPDTB(datadir):
    """
        return annotations from pdtb discourse parser
    """
    TYPE = re.compile('TYPE=\"([^"]*)\"')
    LABEL = re.compile('\sLABEL=\"([^"]*)\"')
    SUBLABEL = re.compile('SUBLABEL=\"([^"]*)\"')
    ID = re.compile('SID=\"([^"]*)\"')
    pdtbFile = open(datadir + "/annotations/pdtb")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    pdtb = AnnotationSet("pdtb")
    i = 0

    for line in pdtbFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        match = TYPE.search(line)
        if match:
            t = match.group(1)

        match = LABEL.search(line)
        if match:
            l = match.group(1)
        else:
            l = None

        match = SUBLABEL.search(line)
        if match:
            sl = match.group(1)
        else:
            sl = None

        match = ID.search(line)
        if match:
            lid = match.group(1)

        a = Annotation(start, end, i, {"TYPE":t, "SID":lid}, lines[start:end])
        if l is not None:
            a.setProp("LABEL",l)

        if sl is not None:
            a.setProp("SUBLABEL",sl)

        pdtb.add(a)
        i += 1
    return pdtb

def getSentences(datadir):
    """Returns a list of annotations of each sentence as detected by
    Reconcile's sentence splitter. """

    sentFile = open(datadir + "/annotations/sent")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    sent = AnnotationSet("sentences")
    i = 0
    for line in sentFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        a = Annotation(start, end, i, {"NUM":i}, lines[start:end])
        sent.add(a)
        i += 1
    return sent

def getHeads(datadir):
    """
    Return an annotation set with the documents "normalized heads"
    """
    HEAD = re.compile('HEAD=\"([^"]*)\"')
    headFile = open(datadir + "/annotations/heads")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    heads = AnnotationSet("heads")

    i = 0
    for line in headFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])

        match = HEAD.search(line)
        if match:
            head = match.group(1)

        a = Annotation(start, end, i, {"HEAD": head}, lines[start:end])
        heads.add(a)
        i += 1

    return heads

def getTextTiles(datadir):
    tileFile = open(datadir + "/annotations/tiles")
    rawTxt = open(datadir + "/raw.txt", 'r')
    lines = ''.join(rawTxt.readlines())
    tiles = AnnotationSet("tiles")
    i = 0
    for line in tileFile:
        line = line.strip()
        tokens = line.split()
        start = int(tokens[1].split(",")[0])
        end = int(tokens[1].split(",")[1])
        a = Annotation(start, end, i, {"NUM":i}, lines[start:end])
        tiles.add(a)
        i += 1
    return tiles

def getAnnotTile(datadir, annot):
    """return the integer of the sentence the annot is found in."""
    tiles = getTextTiles(datadir)
    i = 0
    for t in tiles:
        if t.contains(annot):
            return i
        i += 1
    return -1

def getAnnotSentenceNum(datadir, annot):
    """return the integer of the sentence the annot is found in."""
    sentences = getSentences(datadir)
    i = 0
    for s in sentences:
        if s.contains(annot):
            return i
        i += 1
    return -1

def getAnnotSentence(datadir, annot):
    """return the integer of the sentence the annot is found in."""
    sentences = getSentences(datadir)
    for s in sentences:
        if s.contains(annot):
            return s
    return None

def getTokens(datadir):
    span = re.compile('(\d+),(\d+)')
    tokens = AnnotationSet("tokens")
    tokenFile = open(datadir+"/annotations/token", 'r')
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    i = 0
    for line in tokenFile:
        line=line.strip()
        match = span.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
        tokens.add(Annotation(start, end, i, {}, text))
        i+=1
    return tokens

def getPOS(datadir, addSundance=False):
    """Returns an AnnotationSet with POS for the given document."""
    posFile = open(datadir + "/annotations/postag", 'r')
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    pos = AnnotationSet("parts-of-speech")

    span = re.compile('(\d+),(\d+)')
    i = 0
    for line in posFile:
        line = line.strip()
        attr = {}
        match = span.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
        tokens = line.split()
        tag = tokens[-1]
        attr["TAG"] = tag
        pos.add(Annotation(start, end, i, attr, text))
        i += 1
    posFile.close()

    #if addSundance:
    #    sunPOS = open(datadir + "/annotations/spos", 'r')
    #    for line in sunPOS:
    #        line = line.strip()
    #        match = span.search(line)
    #        if match:
    #            start = int(match.group(1))
    #            end = int(match.group(2))
    #        pos_text = line[line.find("("):line.rfind(")")]

    #        tokens = pos_text.split("(")
    #        tags = []
    #        for t in tokens:
    #            t = t.replace(")", "").strip()
    #            if t != "":
    #                tags.append(t)
    #        pos.addPropBySpan(start, end, "SUN_TAGS", tags)
    #    sunPOS.close()
    return pos

def getGoldNEs(datadir):
    nesFile = open(datadir + "/annotations/gsNEs")
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    span = re.compile('(\d+),(\d+)')
    nes = AnnotationSet("nes")
    i = 0
    for line in nesFile:
        line = line.strip()
        match = span.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
        attr = {}
        tokens = line.split()
        cls = tokens[3]
        attr["NE_CLASS"] = cls
        nes.add(Annotation(start, end, i, attr, text))
        i += 1
    nesFile.close()
    return nes

def getNEs(datadir, addSundance=False):
    """Returns a list of annotations containing all NEs found by the Reconcile
    NE Recognizer. """

    nesFile = open(datadir + "/annotations/ne")
    rawTxt = open(datadir + "/raw.txt", 'r')
    allLines = ''.join(rawTxt.readlines())
    rawTxt.close()
    span = re.compile('(\d+),(\d+)')
    nes = AnnotationSet("nes")
    i = 0
    for line in nesFile:
        line = line.strip()
        match = span.search(line)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            text = allLines[start:end]
        attr = {}
        tokens = line.split()
        cls = tokens[3]
        attr["NE_CLASS"] = cls
        nes.add(Annotation(start, end, i, attr, text))
        i += 1

    if addSundance:
        sunNE = open(datadir + "/annotations/sne", 'r')
        for line in sunNE:
            line = line.strip()
            match = span.search(line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))

            ne_text = line.split("string")[1]
            tokens = ne_text.split()
            tags = []
            for t in tokens:
                tags.append(t)

            nes.addPropBySpan(start, end, "SUN_NE", tags)
        sunNE.close()
    return nes

def getNEsByClass(datadir, cls):
    """Returns a list of annotations according to a supplied semantic class."""
    nes = getNEs(datadir)
    new_nes = []
    for ne in nes:
        if cls in ne.attr["NE_CLASS"]:
            new_nes.append(ne)
    return new_nes

def getPronouns(datadir, options):
    """
        returns a list of pronouns found by reconcile.
        options =>
        STRICT = Only first person pronouns
        POSSESSIVE = Only possessive pronouns
        HARD = Only 'hard' pronouns
        ALL = get only the Reconcile considered pronouns, minus any from the
        'HARD' set.
    """
    nps = getNPs_annots(datadir)
    pronouns = []
    for np in nps:
        text = np.getText().lower()
        if options == "HARD":
            if text in data.HARD_PRONOUNS:
                pronouns.append(np)
        elif options == "POSSESSIVE":
            if text in data.POSSESSIVES:
                pronouns.append(np)
        elif options == "STRICT":
            if text in data.FIRST_PER:
                pronouns.append(np)
        else:
            if (np.getATTR("pronoun") != "NONE") or (text in data.RPRONOUNS):
                pronouns.append(np)
    return pronouns

def getSubjVerb(np, pos):
    for p in pos:
        if np.getEnd() < p.getStart() and p.getATTR("TAG").startswith("V"):
            return p.getText()

def getObjVerb(np, pos):
    verb = ""
    for p in pos:
        if p.getEnd() < np.getStart() and p.getATTR("TAG").startswith("V"):
            verb = p.getText()
    return verb

def prev_sent(sents, np):
    prev = Annotation(-1, -1, -1, {}, "")
    for s in sents:
        if np.getStart() >= s.getStart() and np.getEnd() <= s.getEnd():
            return prev
        else:
            prev = s
    return prev

def next_sent(sents, np):
    for s in sents:
        if np[1] < s[0]:
            return s
    else:
        return Annotation(-1, -1, -1, {}, "")

def NPinS(np, sent):
    if ((np.getStart() >= sent.getStart()) and (np.getEnd() <= sent.getEnd())):
        return True
    else:
        return False
    return False

def nextNP(nps, p):
    """Returns the next np from a list of NPs, does not assume that they are
    sort"""
    nps = sortAnnotsBySpans(nps)
    for i in range(0, len(nps)):
        if (nps[i] == p):
            try:
                return nps[i + 1]
            except:
                return None
    return None

def sent2nps(sent, nps):
    """Returns an annotation set of annotations that contain nps from the sentence
    supplied. """
    tmp = AnnotationSet("nps in sentence")
    for n in nps:
        if n.getStart() >= sent.getStart() and n.getEnd() <= sent.getEnd():
            tmp.add(n)
    return tmp

def sent2nps_prev(sents, nps, np):
    """ """
    s = (-1, -1)
    for sent in sents:
        if np.getStart() >= sent.getStart() and np.getEnd() <= sent.getEnd():
            s = sent
            break
    prev_nps = []
    for n in nps:
        if n.getStart() >= s.getStart() and n.getEnd() <= np.getEnd():
            prev_nps.append(n)
    return prev_nps

def getVerbs(dir):
    """ Return a list of verbs from a given document."""
    verbs = AnnotationSet("verbs")
    posFile = open(dir + "/annotations/postag", 'r')
    txtFile = open(dir + "/raw.txt", 'r')
    rawTxt = ''.join(txtFile.readlines())
    txtFile.close()

    porter = nltk.PorterStemmer()
    num = 0
    for line in posFile:
        line = line.strip()
        tokens = line.split()
        if tokens[3].startswith("V"):
            span = tokens[1]
            start = int(span.split(",")[0])
            end = int(span.split(",")[1])
            text = rawTxt[start:end]

            props = {"pos" : tokens[3].strip()}

            if text.lower() in data.to_be:
                props["to_be"] = True
            else:
                props["to_be"] = False

            stem = porter.stem(text)
            props["stem"] = stem

            verb_class = verbnet.classids(text.lower())
            if verb_class != []:
                props["class"] = verb_class[0]
                #props["roles"] = verbnet.pprint_themeroles(verb_class[0])
                roles = map(string.strip,
                        verbnet.pprint_themroles(verb_class[0]).split("*"))
                props["roles"] = roles[1:]
            else:
                #try it with the stemmed word
                verb_class = verbnet.classids(stem.lower())
                if verb_class != []:
                    props["class"] = verb_class[0] + " (from stemmed)"
                    #props["roles"] = verbnet.pprint_themeroles(verb_class[0])
                    roles = map(string.strip,
                            verbnet.pprint_themroles(verb_class[0]).split("*"))
                    props["roles"] = roles[1:]

            verb = Annotation(start, end, num, props, text)
            verbs.add(verb)
    return verbs

def getAdverbs(docDir):
    adverbs = AnnotationSet("adverbs")
    posFile = open(docDir + "/annotations/postag", 'r')
    txtFile = open(docDir + "/raw.txt", 'r')
    rawTxt = ''.join(txtFile.readlines())
    txtFile.close()

    a_id = 0
    for line in posFile:
        line = line.strip()
        tokens = line.split()
        if tokens[3] in ("RB", "RBR", "RBS"):
            span = tokens[1]
            start = int(span.split(",")[0])
            end = int(span.split(",")[1])
            text = rawTxt[start:end]
            props = {"TEXT" : text, "TAG" : tokens[3]}
            if text.lower() in data.time_adverbs:
                props["CLASS"] = "TIME"
            elif text.lower() in data.manner_adverbs:
                props["CLASS"] = "MANNER"
            elif text.lower() in data.place_adverbs:
                props["CLASS"] = "PLACE"
            elif text.lower() in data.cause_adverbs:
                props["CLASS"] = "CAUSE"
            elif text.lower() in data.modal_adverbs:
                props["CLASS"] = "MODAL"
            else:
                props["CLASS"] = "UNKNOWN"

            adverb = Annotation(start, end, a_id, props, text)
            adverbs.add(adverb)
            a_id += 1
    return adverbs

def getPreps(datadir):
    """annotation set of prepositions """
    prepositions = AnnotationSet("preps")
    posFile = open(datadir + "/annotations/postag")
    #parseFile = open(datadir + "/annotations/parse")
    txtFile = open(datadir + "/raw.txt", 'r')
    rawTxt = ''.join(txtFile.readlines())
    txtFile.close()

    p_id = 0
    for line in posFile:
        line = line.strip()
        tokens = line.split()
        if tokens[3] in ("IN", "AT"):
            span = tokens[1]
            start = int(span.split(",")[0])
            end = int(span.split(",")[1])
            text = rawTxt[start:end]
            props = {"TEXT" : text, "TAG" : tokens[3]}
            prep = Annotation(start, end, p_id, props, text)
            prepositions.add(prep)
    return prepositions

def getPredictions(predictions_file):
    predictions = {}
    with open(predictions_file+"/predictions", 'r') as pred_file:
        for line in pred_file:
            line=line.strip()
            tokens = line.split()
            score = float(tokens[1])
            #tokens2 = tokens[0].split(",")
            #doc = tokens2[0]
            #antecedent = tokens[1]
            #anaphor    = tokens[2]
            predicitions[tokens[0]] = score
    return predicitions

def getProResPairs(f, ft):
    pairs = []
    with open(f+"/raw.txt", 'r') as txtFile:
        wholetext = ''.join(txtFile.readlines())

    with open(f+"/annotations/"+ft, 'r') as pairFile:
        np_id = 0
        for line in pairFile:
            tokens = line.split()
            ant_span = tokens[1]
            ana_span = tokens[2]
            ant_start = int(ant_span.split(",")[0])
            ant_end   = int(ant_span.split(",")[1])
            ant_text  = wholetext[ant_start:ant_end]
            ana_start = int(ana_span.split(",")[0])
            ana_end   = int(ana_span.split(",")[1])
            ana_text  = wholetext[ana_start:ana_end]
            antecedent = Annotation(ant_start, ant_end, np_id, {}, ant_text)
            np_id += 1
            anaphor    = Annotation(ana_start, ana_end, np_id, {}, ana_text)
            np_id += 1
            pairs.append((antecedent, anaphor))
    return pairs

if __name__ == "__main__":
    # test some functionality of this library. 
    nps = getNPs_annots("/home/nathan/Documents/data/promed-test/44")
    for np in nps:
        print np
