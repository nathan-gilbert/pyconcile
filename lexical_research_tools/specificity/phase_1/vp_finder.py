#!/usr/bin/python
# File Name : vp_finder.py
# Purpose :
# Creation Date : 05-16-2013
# Last Modified : Thu 12 Dec 2013 01:46:28 PM MST
# Created By : Nathan Gilbert
#
import sys
import operator
import math
from collections import defaultdict

from pyconcile import reconcile
from pyconcile import utils
from pyconcile.document import Document
from pyconcile.bar import ProgressBar
import specificity_utils
from vp import VirtualPronoun

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

def add_stats(text, head, anaphor, doc, nouns, head2text):

    #catches a problem with the following report
    if head == 'the':
        head = text.split()[-1]

    if head.endswith("%"): return #skip percents
    if head[-1].isdigit(): return #skip numbers
    if utils.isConj(head): return #just skip these guys too
    if head == "himself" : return #NOTE for some reason, the filter doesn't
                                  #catch this, must be happening after head
                                  #noun is created.
    if head == "themselves" : return
    if head == "head" : return
    if head == "where": return
    if head == "there": return
    if head == "here" : return

    anaphor_np = doc.nps.getAnnotBySpan(anaphor.getStart(),
            anaphor.getEnd())

    #update the head2text dict
    if text not in head2text[head]:
        head2text[head].append(text)
    #make sure the head nouns are reasonable
    #print "{0} => {1}".format(text, head)

    #then look for thangs
    if text not in nouns.keys():
        nouns[text] = VirtualPronoun(text)
        nouns[text].updateDocs(doc.getName())
    else:
        nouns[text].updateCount()
        nouns[text].updateDocs(doc.getName())

    if anaphor_np["GRAMMAR"] == "SUBJECT":
        nouns[text].subj += 1
    elif anaphor_np["GRAMMAR"] == "OBJECT":
        nouns[text].dobj += 1

    #begin modifier code
    definite = "the {0}".format(head)
    indefinite1 = "a {0}".format(head)
    indefinite2 = "an {0}".format(head)

    #pos = reconcile.getPOS(doc.getName())
    #head_index = specificity_utils.getHeadIndex(anaphor_np, head)
    #np_pos = pos.getSubset(anaphor.getStart(), anaphor.getEnd())
    #np_words = text.split()
    if text.startswith(definite):
        nouns[text].bare_definite += 1
    #elif text.startswith(indefinite1) or text.startswith(indefinite2):
        #nouns[text].indefinite += 1
    #else:
        ##NOTE: just checking to see if there is some kind of modification now
        #if len(np_pos) == len(np_words):
            ##sys.stderr.write("Mismatch tag and word length: {0} => {1}\n".format(np_pos.getList(), np_words))
            #for i in range(0, head_index):
                #if np_pos[i]["TAG"] == "DT":
                    #continue
                #elif np_pos[i]["TAG"] == "JJ":
                    ##print "Adjective: {0}".format(np_words[i])
                    #nouns[text].adjective_modifiers.append(np_words[i])
                #elif np_pos[i]["TAG"].startswith("N"):
                    ##print "Noun: {0} {1}".format(np_words[i], np_pos[i]["TAG"])
                    #if np_pos[i]["TAG"].startswith("NNP"):
                        #nouns[text].proper_modifiers.append(np_words[i])
                    #else:
                        #nouns[text].common_modifiers.append(np_words[i])
                #else:
                    ##print "?: {0}".format(np_words[i])
                    #nouns[text].other_modifiers.append(np_words[i])

    #if text.startswith("the "):
        #get parts of speech for the np:
    #else:
        ##not definite, but still modified
        #if len(np_pos) == len(np_words):
            ##sys.stderr.write("Mismatch tag and word length: {0} => {1}\n".format(np_pos.getList(), np_words))
            #continue

            #for i in range(0, head_index):
                #if np_pos[i]["TAG"] == "DT":
                    #continue
                #elif np_pos[i]["TAG"] == "JJ":
                    ##print "Adjective: {0}".format(np_words[i])
                    #nouns[text].adjective_modifiers.append(np_words[i])
                #elif np_pos[i]["TAG"].startswith("N"):
                    ##print "Noun: {0} {1}".format(np_words[i], np_pos[i]["TAG"])
                    #if np_pos[i]["TAG"].startswith("NNP"):
                        #nouns[text].proper_modifiers.append(np_words[i])
                    #else:
                        #nouns[text].common_modifiers.append(np_words[i])
                #else:
                    ##print "?: {0}".format(np_words[i])
                    #nouns[text].other_modifiers.append(np_words[i])

    #capture post modifiers
    #if text.find(head + " of ") > -1:
        #of_start = text.find(head + " of ")
        #of_object = text[len(head) + of_start + 3:]
        #nouns[text].of_attachments.append(of_object.strip())

    #if text.find(head + " on ") > -1:
        #of_start = text.find(head + " on ")
        #of_object = text[len(head) + of_start + 3:]
        #nouns[text].on_attachments.append(of_object.strip())

    #if text.find(head + " that ") > -1:
        #that_start = text.find(head + " that ")
        #that_clause = text[len(head) + that_start+5:]
        #nouns[text].that_attachments.append(that_clause.strip())

    #if text.find(head + " with ") > -1:
        #that_start = text.find(head + " with ")
        #that_clause = text[len(head) + that_start+5:]
        #nouns[text].with_attachments.append(that_clause.strip())

    #if text.find(head + " by ") > -1:
        #by_start = text.find(head + " by ")
        #by_object = text[len(head) + by_start+3:]
        #nouns[text].by_attachments.append(by_object.strip())

    #if text.find(head + " which ") > -1:
        #which_start = text.find(head + " which ")
        #which_clause = text[len(head) + which_start+6:]
        #nouns[text].which_attachments.append(which_clause.strip())

    #if len(np_pos) >= head_index+2 and len(np_words) >= head_index+2:
        #if np_pos[head_index+1]["TAG"] == "VBD":
            #nouns[text].verbed.append(np_words[head_index+1])

        #if np_pos[head_index+1]["TAG"] == "VBG":
            #nouns[text].verbing.append(np_words[head_index+1])
    #end modifier code

    #find which chain the anaphor is from and add the chain statistics
    anaphor_chain = None
    for chain in doc.gold_chains.keys():
        for mention in doc.gold_chains[chain]:
            if anaphor == mention:
                anaphor_chain = chain
                break

    chain_name = "{0}:{1}".format(doc.getName(), anaphor_chain)
    if chain_name not in nouns[text].chains:
        nouns[text].chains.append(chain_name)

    if anaphor_chain is not None:
        chain_length = len(doc.gold_chains[anaphor_chain])
        nouns[text].chain_size[doc.getName()] = chain_length

        #coverage
        #chain_start = doc.gold_chains[chain][0].getStart()
        #chain_end   = doc.gold_chains[chain][-1].getEnd()
        #chain_size  = chain_end - chain_start
        #chain_coverage = float(chain_size) / len(doc.text)

        # number of sentences touched / number of sentences
        covered_sentences = 0
        for sent in doc.sentences:
            for mention in doc.gold_chains[anaphor_chain]:
                if sent.contains(mention):
                    covered_sentences += 1
                    break

        chain_coverage = float(covered_sentences) / len(doc.sentences)
        nouns[text].chain_coverage[doc.getName()] = chain_coverage

        for chain in doc.gold_chains.keys():
            if chain == anaphor_chain:
                continue
            if len(doc.gold_chains[chain]) > chain_length:
                break
        else:
            nouns[text].largest_chain += 1

        common_only = True
        for mention in doc.gold_chains[anaphor_chain]:
            if mention == anaphor:
                continue
            mention_head = getHead(utils.textClean(mention.getText()))
            if mention_head not in nouns[text].all_entities:
                nouns[text].all_entities.append(mention_head)

            #does this chain contain proper names?
            mention_np = doc.nps.getAnnotBySpan(mention.getStart(), mention.getEnd())
            if specificity_utils.isProper(mention_np):
                common_only = False

        if chain_name not in nouns[text].nom_chain_only.keys():
            nouns[text].nom_chain_only[chain_name] = common_only
    else:
        sys.stderr.write("Anaphor chain not found?\n")

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
        print "Usage: %s <filelist> +tru" % (sys.argv[0])
        sys.exit(1)

    TRUE_PRONOUNS = True if "+tru" in sys.argv else False
    TRUE = ("he", "she", "her", "him", "it", "they", "them")

    files = []
    with open(sys.argv[1], 'r') as inFile:
        files.extend(filter(lambda x : not x.startswith("#"),
            inFile.readlines()))

    #TODO figure out the stats to match pronoun profiles
    SENT_DIST_3  = 0.50  #70% of antecedents are within 3 sentences
    PRODUCTIVITY = 0.4   #40% of antecedents are different  ~ this is wonky
                        #right now, should remove any string matches or look at the complete chains
                        #instead of only the most recent antecedent
    PRODUCTIVITY2= 0.6  #
    STARTS_CHAIN = 0.25  #this word starts chains very infrequently
    ANTE_SUBJ    = 0.5   #the antecedent is a subj over half the time
    SELF_SUBJ    = 0.5   #the noun is a subj over half the time
    AIDF         = 2.63  #the average idf is lower than 3.33

    #text -> class
    nouns = {}

    #head -> texts
    #this will allow for collapsing down on head nouns if I want to.
    head2text = defaultdict(list)

    sys.stderr.flush()
    sys.stderr.write("\r")
    prog = ProgressBar(len(files))
    i = 0
    docs_needed = round(float(len(files)) * 0.05)
    for f in files:
        if f.startswith("#"): continue

        prog.update_time(i)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()

        i += 1
        f=f.strip()
        doc = Document(f)
        gold_nps = reconcile.getNPs(f)
        gold_chains = reconcile.getGoldChains(f)
        ace_annots = reconcile.parseGoldAnnots(f)
        doc.addGoldChains(gold_chains)

        for np in gold_nps:
            text = utils.textClean(np.getText().lower()).strip()
            if TRUE_PRONOUNS:
                if text in TRUE:
                    head = text
                    add_stats(text, head, np, doc, nouns, head2text)
            else:
                #if specificity_utils.isNominal(np):
                #head = getHead(text)
                ace_np = ace_annots.getAnnotBySpan(np.getStart(), np.getEnd())
                head = ace_np["HEAD"].lower()
                if not ace_np["GOLD_SINGLETON"] and ace_np["is_nominal"]:
                    #head = getHead(text)
                    #if head.endswith("%"): continue #skip percents
                    #if head[-1].isdigit(): continue #skip numbers
                    #if utils.isConj(head): continue #just skip these guys too
                    add_stats(text, head, np, doc, nouns, head2text)

    sys.stderr.write("\r \r\n")

    head_counts = {}
    for head in head2text.keys():
        total_count = 0
        for text in head2text[head]:
            total_count += nouns[text].count
        head_counts[head] = total_count

    sorted_head_counts = sorted(head_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    print "{0:17} {1:3} {2:3} {3:5} {4:5} {5:4} {6:4} {7:4} {8:4} {9:4} {10:4} {11:4} {12:4} {13:>4} {14:>4} {15:>4} {16:>4}".format("head","C","d","MD","MMD", "D3", "nPr", "aPr", "ba","As", "ss", "prp", "nc","Cs", "Cc","aidf", "bd")
    print

    for hc in sorted_head_counts:
        total_zero_sentence = 0
        total_one_sentence  = 0
        total_two_sentence  = 0
        total_three_sentence= 0
        total_productivity  = 0
        total_productivity2 = []
        total_chains        = []
        total_chain_starts  = 0
        total_nom_chains    = {}
        total_antecedents   = 0
        total_subj_ante     = 0
        total_dobj_ante     = 0
        total_is_subj       = 0
        total_is_dobj       = 0
        total_string_matches= 0
        total_prp_ante      = 0
        total_pro_ante      = 0
        total_nom_ante      = 0
        total_bare_def      = 0
        total_adj_mods      = 0
        total_prp_mods      = 0
        total_nom_mods      = 0
        total_oth_mods      = 0
        total_docs          = {}
        chain_sizes         = []
        chain_coverage      = []

        for text in head2text[hc[0]]:
            total_zero_sentence += nouns[text].zero_sentence
            total_one_sentence  += nouns[text].one_sentence
            total_two_sentence  += nouns[text].two_sentence
            total_three_sentence+= nouns[text].three_sentence
            total_productivity  += nouns[text].productivity()
            total_productivity2.extend(nouns[text].all_entities)
            #total_chains       += len(nouns[text].most_recent_antecedents)
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
            total_bare_def      += nouns[text].bare_definite
            total_adj_mods      += len(nouns[text].adjective_modifiers)
            total_prp_mods      += len(nouns[text].proper_modifiers)
            total_nom_mods      += len(nouns[text].common_modifiers)
            total_oth_mods      += len(nouns[text].other_modifiers)

            #total_nom_chains    += len(filter(lambda x : x, nouns[text].nom_chain_only))
            chain_sizes.append(float(sum(nouns[text].chain_size.values())) / len(nouns[text].docs.keys()))
            chain_coverage.append(float(sum(nouns[text].chain_coverage.values())) / len(nouns[text].docs.keys()))
            #count up all the chains
            for chain in nouns[text].chains:
                if chain not in total_chains:
                    total_chains.append(chain)
            for key in nouns[text].docs.keys():
                total_docs[key] = total_docs.get(key, 0) + nouns[text].docs[key]

            for key in nouns[text].nom_chain_only.keys():
                total_nom_chains[key] = nouns[text].nom_chain_only[key]

        if len(total_docs) < docs_needed:
            continue

        mean_chain_size = float(sum(chain_sizes)) / len(chain_sizes)
        mean_chain_coverage = float(sum(chain_coverage)) / len(chain_coverage)

        tf = []
        for key in total_docs.keys():
            d_tf = (1 + math.log(total_docs[key])) #* math.log(float(len(files))) # / len(total_docs.keys()))
            tf.append(d_tf)
        mean_tf_idf = (float(sum(tf)) / len(tf)) * math.log(float(len(files)) / len(total_docs.keys()))

        total_one_sentence += total_zero_sentence
        total_two_sentence += total_one_sentence
        total_three_sentence+= total_two_sentence

        mentions_per_doc        = float(head_counts[hc[0]]) / len(total_docs.keys())
        median_mentions_per_doc = specificity_utils.median(total_docs.values())
        pro_count = 0

        #total_mods = total_adj_mods + total_prp_mods + total_nom_mods + total_oth_mods
        #try:
        #    percentage_of_adj_mods  = float(total_adj_mods) / total_mods
        #    percentage_of_prp_mods  = float(total_prp_mods) / total_mods
        #    percentage_of_nom_mods  = float(total_nom_mods) / total_mods
        #    percentage_of_oth_mods  = float(total_oth_mods) / total_mods
        #except:
        #    percentage_of_adj_mods  = 0.0
        #    percentage_of_prp_mods  = 0.0
        #    percentage_of_nom_mods  = 0.0
        #    percentage_of_oth_mods  = 0.0
        #percentage_of_premods   = float(total_adj_mods + total_prp_mods + total_nom_mods) / head_counts[hc[0]]

        try:
            proper_antecedent = float(total_prp_ante) / total_antecedents
        except:
            proper_antecedent = 0.0

        #print "Nom chains: {0}".format(len(filter(lambda x : x, total_nom_chains.values())))
        #print "Total chains: {0}".format(len(total_chains))
        nom_chain_percentage = float(len(filter(lambda x : x, total_nom_chains.values()))) / len(total_chains)

        #criteria 1
        sent_3 = float(total_three_sentence) / head_counts[hc[0]]
        #if sent_3 >= SENT_DIST_3:
        #    pro_count += 1

        #criteria 2
        #old way
        try:
            prod = float(total_productivity) / total_antecedents # the number of unique closest antecedents over the total number of closest antecedents
        except:
            prod = 0.0
        prod2 = float(len(set(total_productivity2))) / len(total_chains) #the total number of unique antecedents over the total number of chains

        #if prod2 >= PRODUCTIVITY2:
        #    pro_count += 1

        #if prod >= PRODUCTIVITY:
        #    pro_count += 1

        #criteria 3
        ba = float(total_chain_starts) / head_counts[hc[0]]
        #if ba <= STARTS_CHAIN:
        #    pro_count += 1

        #criteria 4 
        try:
            ante_subj = float(total_subj_ante) / total_antecedents
        except:
            ante_subj = 0.0

        #if ante_subj >= ANTE_SUBJ:
        #    pro_count += 1

        #criteria 5 
        self_sub =  float(total_is_subj) / head_counts[hc[0]]
        #if self_sub >= SELF_SUBJ:
        #    pro_count += 1

        #criteria 6
        #if mean_tf_idf <= AIDF:
        #    pro_count += 1

        #print "{0:15} :C: {1:>3} :D: {2:>3} ({3:.2f}) : {4:>3} ({5:.2f}) : {6:>3} ({7:.2f}) :P: {8:.2f} :Pi: {9:5.2f} :Str: {10:.2f} :BA: {11:.2f} :A_s: {12:.2f} :A_o: {13:.2f} :S: {14:.2f} :O: {15:.2f}".format(
        #print "{0:15} :C: {1:3} :D: {2:.2f} : {3:.2f} : {4:.2f} :P: {5:.2f} :Pi: {6:5.2f} :st: {7:.2f} :1: {8:.2f} :As: {9:.2f} :Ao: {10:.2f} :s: {11:.2f} :o: {12:.2f} :n: {13:.2f} :pr: {14:.2f} :pn: {15:.2f}".format( 

        label = ""
        if pro_count > 0: #and not TRUE_PRONOUNS:
            label = "*={0}".format(pro_count)

        #hc[1] and head_counts[hc[0]] should be the same thing...
        print "{0:15} {1:4} {2:3} {3:5.2f} {4:5.2f} {5:.2f} {6:.2f} {7:.2f} {8:.2f} {9:.2f} {10:.2f} {11:.2f} {12:.2f} {13:5.2f} {14:.2f} {15:.2f} {16:.2f} {17}".format(
                hc[0],
                hc[1],
                len(total_docs.keys()),
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
                prod2,
                #float(total_antecedents) / total_productivity,
                #float(total_string_matches) / total_antecedents,
                #float(total_chain_starts) / head_counts[hc[0]],
                ba,
                #float(total_subj_ante) / total_antecedents,
                ante_subj,
                #float(total_dobj_ante) / total_antecedents,
                float(total_is_subj) / head_counts[hc[0]],
                #float(total_is_dobj) / head_counts[hc[0]],
                #float(total_nom_ante) / total_antecedents,
                proper_antecedent,
                nom_chain_percentage,
                #float(total_pro_ante) / total_antecedents,
                mean_chain_size,
                mean_chain_coverage,
                mean_tf_idf,
                float(total_bare_def) / head_counts[hc[0]],
                #percentage_of_premods,
                #percentage_of_adj_mods,
                #percentage_of_prp_mods,
                #percentage_of_nom_mods,
                label
                )
        #print

