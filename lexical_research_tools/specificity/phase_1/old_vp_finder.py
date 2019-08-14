#!/usr/bin/python
# File Name : vp_finder.py
# Purpose :
# Creation Date : 05-16-2013
# Last Modified : Wed 12 Jun 2013 04:13:53 PM MDT
# Created By : Nathan Gilbert
#
import sys
import operator
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import utils
from pyconcile.document import Document
from pyconcile.bar import ProgressBar
import specificity_utils

class Nominal:
    def __init__(self, t):
        self.text = t
        self.count = 1
        self.docs = {}
        self.most_recent_antecedents = []
        self.string_matches= 0
        self.zero_sentence = 0
        self.one_sentence  = 0
        self.two_sentence  = 0
        self.large_distance= 0
        self.starts_chain  = 0
        self.subj_ante     = 0
        self.dobj_ante     = 0
        self.subj          = 0
        self.dobj          = 0
        self.prp_ante      = 0
        self.pro_ante      = 0
        self.nom_ante      = 0

        #future stuff
        #if a word is modified or not may affect its vp status
        self.modifiers = []

    def updateCount(self):
        self.count += 1

    def updateDocs(self, d):
        self.docs[d] = self.docs.get(d, 0) + 1

    def sentence_distance(self, sd):
        if sd == 0:
            self.zero_sentence += 1
        elif sd == 1:
            self.one_sentence += 1
        elif sd == 2:
            self.two_sentence += 1
        else:
            self.large_distance += 1

    def productivity(self):
        return len(set(self.most_recent_antecedents))

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

        #capture possessives?
        #if (word.endswith("'s"):
        #   new_text = ""
        #   continue

        new_text += word + " "
        first = False

    new_text = new_text.strip()
    if new_text == "":
        sys.stderr.write("Empty text: \"{0}\" : \"{1}\"".format(text, new_text))

    return new_text.split()[-1]

def add_stats(text, anaphor, doc, nouns, head2text):
    head = getHead(text)
    if head.endswith("%"): return #skip percents
    if head[-1].isdigit(): return #skip numbers
    if utils.isConj(head): return #just skip these guys too
    if head == "himself" : return #NOTE for some reason, the filter doesn't
                                  #catch this, must be happening after head
                                  #noun is created.
    if head == "themselves" : return

    anaphor_np = doc.nps.getAnnotBySpan(anaphor.getStart(),
            anaphor.getEnd())

    #update the head2text dict
    if text not in head2text[head]:
        head2text[head].append(text)
    #make sure the head nouns are reasonable
    #print "{0} => {1}".format(text, head)

    #then look for thangs
    if text not in list(nouns.keys()):
        nouns[text] = Nominal(text)
        nouns[text].updateDocs(doc.getName())
    else:
        nouns[text].updateCount()
        nouns[text].updateDocs(doc.getName())

    if anaphor_np["GRAMMAR"] == "SUBJECT":
        nouns[text].subj += 1
    elif anaphor_np["GRAMMAR"] == "OBJECT":
        nouns[text].dobj += 1

    antecedent = doc.closest_antecedent(anaphor)
    if antecedent is not None:
        #record stats
        sd = doc.sentence_distance(antecedent, anaphor)
        nouns[text].sentence_distance(sd)
        nouns[text].most_recent_antecedents.append(antecedent.getText().lower())

        antecedent_np = doc.nps.getAnnotBySpan(antecedent.getStart(),
                antecedent.getEnd())
        if antecedent_np["GRAMMAR"] == "SUBJECT":
            nouns[text].subj_ante += 1
        elif antecedent_np["GRAMMAR"] == "OBJECT":
            nouns[text].dobj_ante += 1

        if antecedent.getText().lower() == anaphor.getText().lower():
            nouns[text].string_matches += 1

        if specificity_utils.isProper(antecedent_np):
            nouns[text].prp_ante += 1
        elif specificity_utils.isNominal(antecedent_np):
            nouns[text].nom_ante += 1
        elif specificity_utils.isPronoun(antecedent_np):
            nouns[text].pro_ante += 1

    else:
        #this guy starts the chain
        nouns[text].starts_chain += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist> +tru" % (sys.argv[0]))
        sys.exit(1)

    TRUE_PRONOUNS = True if "+tru" in sys.argv else False
    TRUE = ("he", "she", "her", "him", "it", "they", "them")

    files = []
    with open(sys.argv[1], 'r') as inFile:
        files.extend([x for x in inFile.readlines() if not x.startswith("#")])

    #TODO figure out the stats to match pronoun profiles
    SENT_DIST_3 = 0.75  #90% of antecedents are within 3 sentences
    PRODUCTIVITY= 0.67  #80% of antecedents are different 
    STARTS_CHAIN= 0.25  #this word starts chains very infrequently
    ANTE_SUBJ   = 0.5   #the antecedent is a subj over half the time

    #text -> class
    nouns = {}

    #head -> texts
    #this will allow for collapsing down on head nouns if I want to.
    head2text = defaultdict(list)

    #sys.stdout.flush()
    #sys.stdout.write("\r")
    #prog = ProgressBar(len(files))
    i = 0
    for f in files:
        if f.startswith("#"): continue

        #prog.update_time(i)
        #sys.stdout.write("\r%s" % (str(prog)))
        #sys.stdout.flush()

        i += 1
        f=f.strip()
        doc = Document(f)
        gold_nps = reconcile.getNPs(f)
        gold_chains = reconcile.getGoldChains(f)
        doc.addGoldChains(gold_chains)

        for np in gold_nps:
            text = utils.textClean(np.getText().lower()).strip()
            if TRUE_PRONOUNS:
                if text in TRUE:
                    add_stats(text, np, doc, nouns, head2text)
            else:
                if specificity_utils.isNominal(np):
                    #head = getHead(text)
                    #if head.endswith("%"): continue #skip percents
                    #if head[-1].isdigit(): continue #skip numbers
                    #if utils.isConj(head): continue #just skip these guys too
                    add_stats(text, np, doc, nouns, head2text)

    #sys.stdout.write("\r \r\n")
    #sorted_nouns = sorted(nouns, key=operator.attrgetter('count'), reverse=True)
    #sorted_nouns = sorted(nouns.values(), key=operator.attrgetter('count'), reverse=True)
    #print sorted_nouns
    #for nom in sorted_nouns:
    #    print "{0:3} : {1}".format(nom.count, nom.text)

    head_counts = {}
    for head in list(head2text.keys()):
        total_count = 0
        for text in head2text[head]:
            total_count += nouns[text].count
        head_counts[head] = total_count

    sorted_head_counts = sorted(iter(head_counts.items()), key=operator.itemgetter(1), reverse=True)
    print("{0:17} {1:3} {2:3} {3:5} {4:5} {5:4} {6:4} {7:4} {8:4} {9:4} {10:4} {11:4} {12:4} {13:4} {14:4} {15:4}".format("head", "C","d", "MD","MMD", "D2", "Pr", "st", "ba", "As", "Ao", "ss", "so", "nm", "pr", "pn"))
    print()
    for hc in sorted_head_counts:
        #stop if count less than 5
        if hc[1] < 5:
            break

        total_zero_sentence = 0
        total_one_sentence  = 0
        total_two_sentence  = 0
        total_productivity  = 0
        total_chain_starts  = 0
        total_antecedents   = 0
        total_subj_ante     = 0
        total_dobj_ante     = 0
        total_is_subj       = 0
        total_is_dobj       = 0
        total_string_matches= 0
        total_prp_ante      = 0
        total_pro_ante      = 0
        total_nom_ante      = 0
        total_docs          = {}

        for text in head2text[hc[0]]:
            total_zero_sentence += nouns[text].zero_sentence
            total_one_sentence  += nouns[text].one_sentence
            total_two_sentence  += nouns[text].two_sentence
            total_productivity  += nouns[text].productivity()
            total_chain_starts  += nouns[text].starts_chain
            total_antecedents   += len(nouns[text].most_recent_antecedents)
            total_subj_ante     += nouns[text].subj_ante
            total_dobj_ante     += nouns[text].dobj_ante
            total_is_subj       += nouns[text].subj
            total_is_dobj       += nouns[text].dobj
            total_string_matches+= nouns[text].string_matches
            total_prp_ante      += nouns[text].prp_ante
            total_pro_ante      += nouns[text].pro_ante
            total_nom_ante      += nouns[text].nom_ante
            for key in list(nouns[text].docs.keys()):
                total_docs[key] = total_docs.get(key, 0) + nouns[text].docs[key]

        if len(total_docs) < 3:
            continue

        total_one_sentence += total_zero_sentence
        total_two_sentence += total_one_sentence

        mentions_per_doc        = float(head_counts[hc[0]]) / len(list(total_docs.keys()))
        median_mentions_per_doc = specificity_utils.median(list(total_docs.values()))

        pro_count = 0

        #criteria 1
        sent_3 = float(total_two_sentence) / head_counts[hc[0]]
        if sent_3 >= SENT_DIST_3:
            pro_count += 1

        #criteria 2
        prod = float(total_productivity) / total_antecedents
        if prod >= PRODUCTIVITY:
            pro_count += 1

        #criteria 3
        ba = float(total_chain_starts) / head_counts[hc[0]]
        if ba <= STARTS_CHAIN:
            pro_count += 1

        #criteria 4
        ante_subj = float(total_subj_ante) / total_antecedents
        if ante_subj >= ANTE_SUBJ:
            pro_count += 1

        #print "{0:15} :C: {1:>3} :D: {2:>3} ({3:.2f}) : {4:>3} ({5:.2f}) : {6:>3} ({7:.2f}) :P: {8:.2f} :Pi: {9:5.2f} :Str: {10:.2f} :BA: {11:.2f} :A_s: {12:.2f} :A_o: {13:.2f} :S: {14:.2f} :O: {15:.2f}".format(
        #print "{0:15} :C: {1:3} :D: {2:.2f} : {3:.2f} : {4:.2f} :P: {5:.2f} :Pi: {6:5.2f} :st: {7:.2f} :1: {8:.2f} :As: {9:.2f} :Ao: {10:.2f} :s: {11:.2f} :o: {12:.2f} :n: {13:.2f} :pr: {14:.2f} :pn: {15:.2f}".format( 

        label = ""
        if pro_count > 0: #and not TRUE_PRONOUNS:
            label = "*={0}".format(pro_count)


        print("{0:15} {1:3} {2:3} {3:5.2f} {4:5.2f} {5:.2f} {6:.2f} {7:.2f} {8:.2f} {9:.2f} {10:.2f} {11:.2f} {12:.2f} {13:.2f} {14:.2f} {15:.2f} {16}".format(
                hc[0],
                hc[1],
                len(set(total_docs)),
                #total_zero_sentence,
                #float(total_zero_sentence) / head_counts[hc[0]],
                #total_one_sentence,
                #float(total_one_sentence) / head_counts[hc[0]],
                #total_two_sentence,
                #float(total_two_sentence) / head_counts[hc[0]],
                mentions_per_doc,
                median_mentions_per_doc,
                sent_3,
                #float(total_productivity) / total_antecedents,
                prod,
                #float(total_antecedents) / total_productivity,
                float(total_string_matches) / total_antecedents,
                #float(total_chain_starts) / head_counts[hc[0]],
                ba,
                #float(total_subj_ante) / total_antecedents,
                ante_subj,
                float(total_dobj_ante) / total_antecedents,
                float(total_is_subj) / head_counts[hc[0]],
                float(total_is_dobj) / head_counts[hc[0]],
                float(total_nom_ante) / total_antecedents,
                float(total_prp_ante) / total_antecedents,
                float(total_pro_ante) / total_antecedents,
                label
                ))
        #print

