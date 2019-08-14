#!/usr/bin/python
# File Name : corpora_statistics.py
# Purpose : Generate a set of statistics over a given corpus
# Creation Date : 03-15-2012
# Last Modified : Fri 16 Mar 2012 07:11:17 PM MDT
# Created By : Nathan Gilbert
#
#DONE # of coref chains
#DONE # of resolutions
#DONE # of docs
#DONE # of gold markables
#DONE approx: sentences, types, tokens, tiles, tokens per sentence
#DONE proportion of common->common, proper->common, etc resolutions
#DONE find first closest resolution type, defined as the closest antecedent
#     to a given anaphor
#DONE NE class distribution
#TODO further feature breakdown [how many appositive matches, string matches,
#      predicate nominals, etc. 
import sys
import string
import operator

import nltk
import nltk.data

from pyconcile import reconcile
from pyconcile import utils
from pyconcile import feature_utils
from pyconcile.bar import ProgressBar

def resolution_type(anaphor, antecedent):
    """
    returns a string contain the type of this resolution

    @param anaphor_type: the type of markable the anaphor is
    @param antecedent_type: the type of markable the antecedent is
    """

    if anaphor.getATTR("is_nominal"):
        if antecedent.getATTR("is_nominal"):
            return "common2common"
        elif antecedent.getATTR("is_proper"):
            return "common2proper"
        else:
            return "common2pronoun"
    elif anaphor.getATTR("is_proper"):
        if antecedent.getATTR("is_nominal"):
            return "proper2common"
        elif antecedent.getATTR("is_proper"):
            return "proper2proper"
        else:
            return "proper2pronoun"
    elif anaphor.getATTR("is_pronoun"):
        if antecedent.getATTR("is_nominal"):
            return "pronoun2common"
        elif antecedent.getATTR("is_proper"):
            return "pronoun2proper"
        else:
            return "pronoun2pronoun"
    else:
        return None

def process_raw_txt(txt, st):
    """
    Processes a txt file via nltk, return dict of stats

    @param txt: text to process
    @type txt: string
    @param st: sentence tokenizer
    @type st: nltk sentence tokenizer model
    """
    stats = {"sentences" : 0, "tokens" : 0}
    sents = st.tokenize(txt)
    stats["sentences"] += len(sents)
    for s in sents:
        tokens = nltk.word_tokenize(s)
        stats["tokens"] += len(tokens)
    return stats

def get_doc_types(txt):
    """
    Find all the types (as opposed to tokens...)

    """
    types = {}
    tokens = nltk.word_tokenize(txt)
    for t in tokens:
        types[t] = types.get(t, 0) + 1
    return types

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <indir> <filelist>" % (sys.argv[0])
        sys.exit(1)

    with open(sys.argv[2], 'r') as file_list:
        files = map(string.strip, file_list.readlines())

    total_coref_chains = 0       #total # of chains
    total_gold_markables = 0     #sum chain_length
    max_resolutions_possible = 0 #sum( chain_length * chain_length-1 / 2)
    min_resolutions_possible = 0 #sum(chain_length - 1)
    total_docs = len(files)
    total_feature_pairs = 0

    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    ttt = nltk.tokenize.TextTilingTokenizer()

    d=0
    corpus_stats = {}
    corpus_stats["common2common"] = 0
    corpus_stats["common2proper"] = 0
    corpus_stats["common2pronoun"] = 0
    corpus_stats["proper2common"] = 0
    corpus_stats["proper2proper"] = 0
    corpus_stats["proper2pronoun"] = 0
    corpus_stats["pronoun2common"] = 0
    corpus_stats["pronoun2proper"] = 0
    corpus_stats["pronoun2pronoun"] = 0
    corpus_stats["1_common2common"] = 0
    corpus_stats["1_common2proper"] = 0
    corpus_stats["1_common2pronoun"] = 0
    corpus_stats["1_proper2common"] = 0
    corpus_stats["1_proper2proper"] = 0
    corpus_stats["1_proper2pronoun"] = 0
    corpus_stats["1_pronoun2common"] = 0
    corpus_stats["1_pronoun2proper"] = 0
    corpus_stats["1_pronoun2pronoun"] = 0
    corpus_types = {}
    corpus_nes = {}
    corpus_sundance_nes = {}

    fdir = "features.goldnps"
    prog = ProgressBar(len(files))

    print "Processing documents..."
    for f in files:
        d+=1
        #progress bar updates
        sys.stdout.write("\r")
        prog.update_time(d)
        sys.stdout.write("\r%s" % (str(prog)))
        sys.stdout.flush()
        #print "Processing document %d/%d" % (d, len(files))
        gold_chains = reconcile.getGoldChains(sys.argv[1]+"/"+f)
        total_coref_chains += len(gold_chains.keys())

        with open(sys.argv[1]+"/"+f+"/raw.txt", 'r') as raw_txt_file:
            raw_txt = ''.join(raw_txt_file.readlines())

        nps = reconcile.getNPs(sys.argv[1]+"/"+f)
        nes = reconcile.getNEs(sys.argv[1]+"/"+f)
        sun_nes = reconcile.getSundanceNEs(sys.argv[1]+"/"+f)
        features = feature_utils.getFeatures(sys.argv[1]+"/"+f, fdir)
        total_feature_pairs += len(features.keys())

        doc_stats = {}
        doc_stats = process_raw_txt(raw_txt, sent_tokenizer)
        doc_stats["common2common"] = 0
        doc_stats["common2proper"] = 0
        doc_stats["common2pronoun"] = 0
        doc_stats["proper2common"] = 0
        doc_stats["proper2proper"] = 0
        doc_stats["proper2pronoun"] = 0
        doc_stats["pronoun2common"] = 0
        doc_stats["pronoun2proper"] = 0
        doc_stats["pronoun2pronoun"] = 0
        doc_stats["1_common2common"] = 0
        doc_stats["1_common2proper"] = 0
        doc_stats["1_common2pronoun"] = 0
        doc_stats["1_proper2common"] = 0
        doc_stats["1_proper2proper"] = 0
        doc_stats["1_proper2pronoun"] = 0
        doc_stats["1_pronoun2common"] = 0
        doc_stats["1_pronoun2proper"] = 0
        doc_stats["1_pronoun2pronoun"] = 0

        try:
            tiles = ttt.tokenize(raw_txt)
        except ValueError:
            tiles = [raw_txt]

        doc_stats["tiles"] = len(tiles)

        doc_types = get_doc_types(raw_txt)
        for t in doc_types:
            if t in corpus_types.keys():
                corpus_types[t] += doc_types[t]
            else:
                corpus_types[t] = doc_types[t]

        #loop over chains
        for key in gold_chains.keys():
            chain = gold_chains[key]
            total_gold_markables += len(chain)
            max_resolutions_possible += ((len(chain)**2 - len(chain)) / 2)
            min_resolutions_possible += len(chain) - 1

            #gather the NE information
            for mention in chain:
                #first for Standfor NER
                for ne in nes:
                    if ne.getStart() >= mention.getStart() \
                        and ne.getEnd() <= mention.getEnd():
                        sem_start = ne.getStart() - mention.getStart()
                        if not utils.spanInPrep(sem_start, mention.getText()):
                            corpus_nes[ne.getATTR("NE_CLASS")] =\
                            corpus_nes.get(ne.getATTR("NE_CLASS"), 0) + 1
                #then for Sundance Semantic dictionary
                for ne in sun_nes:
                    if ne.getATTR("SUN_NE") == "ENTITY":
                        continue
                    if ne.getStart() >= mention.getStart() \
                        and ne.getEnd() <= mention.getEnd():
                        sem_start = ne.getStart() - mention.getStart()
                        if not utils.spanInPrep(sem_start, mention.getText()):
                            corpus_sundance_nes[ne.getATTR("SUN_NE")] =\
                            corpus_sundance_nes.get(ne.getATTR("SUN_NE"), 0) + 1

            #loop over the mentions in chain
            for i in range(len(chain)-1, 0, -1):
                anaphor = chain[i]
                for j in range(i-1,  -1,  -1):
                    antecedent = chain[j]
                    #find out the resolution type
                    rez_type = resolution_type(anaphor, antecedent)
                    if rez_type is None:
                        #we can really say anything about what type
                        #resolution this is
                        #print "Unknown pair type"
                        doc_stats["other"] = doc_stats.get("other", 0) + 1
                    else:
                        doc_stats[rez_type] += 1
                        if ((i-j) == 1):
                            #we have the closest possible resolution
                            doc_stats["1_"+rez_type] += 1

                    #let's grab the features now:
                    #first grab the proper ids from the reconcile side...
                    ant_id = nps.getAnnotBySpan(antecedent.getStart(),
                            antecedent.getEnd()).getID()
                    ana_id = nps.getAnnotBySpan(anaphor.getStart(),
                            anaphor.getEnd()).getID()

                    fkey = "%d,%d" % (ant_id, ana_id)
                    deseridata = ("Prednom", "Appositive", "SoonStr",
                            "WordsStr", "WordOverlap", "Modifier", "WordsSubstr",
                            "BothProperNouns", "BothSubjects", "Animacy",
                            "Gender", "Number", "Alias", "WordNetClass",
                            "WNSynonyms", "HeadMatch", "ProResolve",
                            "RuleResolve", "Syntax", "Constraints")

                    #NOTE some keys are not found, but they appear to be from
                    #cases where the antecedent appears "later" in the document
                    #than the anaphor because reconcile labelling IDs
                    #incorrectly.
                    if fkey in features.keys():
                        for fname in deseridata:
                            if feature_utils.feature_name_to_bool(fname,
                                    fkey, features):
                                kk="feature_%s" % fname
                                doc_stats[kk] = \
                                doc_stats.get(kk, 0) + 1

                        #pred_nom = True if features[feat_key].get("Prednom", 0.0) > 0 else False
                        #appos = True if features[feat_key].get("Appositive", 0.0) > 0 else False
                        #if pred_nom:
                            #doc_stats["feature_prednom"] = \
                            #doc_stats.get("feature_prednom", 0) + 1
                        #if appos:
                            #doc_stats["feature_appositive"] = \
                            #doc_stats.get("feature_appositive", 0) + 1


        #copy the doc stats to the corpus wide stats dictionary
        for key in doc_stats.keys():
            if key in corpus_stats.keys():
                corpus_stats[key] += doc_stats[key]
            else:
                corpus_stats[key] = doc_stats[key]

    sys.stdout.write("\r \r\n")
    print "===================================="
    print "%s corpus statistics" % (sys.argv[1])
    print "Total documents: %d" % total_docs
    print "Totals and Averages:"
    print " Coref Chains:       %5d" % total_coref_chains
    print " Chain/Doc:          %3.2f" % (total_coref_chains/float(total_docs))
    print " Chain Len Avg:      %3.2f" % \
    (total_gold_markables/float(total_coref_chains))
    print " Markables:          %5d" % total_gold_markables
    print " Mark/Doc:           %3.2f" % (total_gold_markables/float(total_docs))
    print " Feature Pairs:      %5d" % (total_feature_pairs)
    print " Max Rez:            %5d (%3.2f)" % (max_resolutions_possible,
            max_resolutions_possible/float(total_feature_pairs))
    print " Min Rez:            %5d" % min_resolutions_possible
    print " Total Stanford NEs: %5d" % (sum(corpus_nes.values()))
    print " Total Sundance NEs: %5d" % (sum(corpus_sundance_nes.values()))
    print " Total tokens:       %5d" % corpus_stats["tokens"]
    print " Tokens/Doc:         %3.2f" % \
    (corpus_stats["tokens"]/float(total_docs))
    del corpus_stats["tokens"]
    print " Total types:        %5d" % len(corpus_types.keys())
    print " Types/Doc:          %3.2f" % \
    (len(corpus_types.keys())/float(total_docs))
    print " Total sentences:    %5d" % corpus_stats["sentences"]
    print " Sent/Doc:           %3.2f" % \
    (corpus_stats["sentences"]/float(total_docs))
    del corpus_stats["sentences"]
    print " Total Tiles:        %5d" % (corpus_stats["tiles"])
    print " Tiles/Doc:          %3.2f" % (corpus_stats["tiles"]/float(total_docs))
    del corpus_stats["tiles"]
    print "-----------------------------------"
    print "Feature statistics"
    remove_keys=[]
    for key in corpus_stats.keys():
        if key.startswith("feature_"):
            remove_keys.append(key)
    remove_keys=sorted(remove_keys)
    for key in remove_keys:
        print "%20s -> %6d (%3.2f)" % (key.replace("feature_",""),
                    corpus_stats[key],
                    corpus_stats[key]/float(total_feature_pairs))
    for key in remove_keys:
        del corpus_stats[key]
    print "-----------------------------------"
    print "Resolution statistics"

    keys = sorted(corpus_stats.keys())
    for key in keys:
        print "%20s -> %6d (%3.2f) (%3.2f)" % (key, corpus_stats[key],
                corpus_stats[key]/float(total_docs),
                corpus_stats[key]/float(max_resolutions_possible))
    print "-----------------------------------"
    print "NE statistics"
    sorted_nes = sorted(corpus_nes.iteritems(), key=operator.itemgetter(1),
            reverse=True)
    for p in sorted_nes:
        print "%20s -> %6d" % (p[0], p[1])
    #keys = sorted(corpus_nes.keys())
    #for key in keys:
    #    print "%20s -> %6d" % (key, corpus_nes[key])
    print "-----------------------------------"
    sorted_sundance_nes = sorted(corpus_sundance_nes.iteritems(),
            key=operator.itemgetter(1), reverse=True)
    for p in sorted_sundance_nes:
        print "%30s -> %6d" % (p[0], p[1])
    #keys = sorted(corpus_sundance_nes.keys())
    #for key in keys:
        #print "%30s -> %d" % (key, corpus_sundance_nes[key])

    print "-----------------------------------"
