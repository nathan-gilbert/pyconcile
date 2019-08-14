#!/usr/bin/python
# File Name : qp-finder.py
# Purpose : This is a script to hunt out the characteristics of common noun
# instances that are in close proximity to their antecedents.
# Creation Date : 12-12-2013
# Last Modified : Wed 29 Jan 2014 02:39:05 PM MST
# Created By : Nathan Gilbert
#
import sys
import time
import datetime
from optparse import OptionParser

from pyconcile import reconcile
from pyconcile import utils
from pyconcile.bar import ProgressBar
from qp import QuasiPronoun
import qp_utils

#TODO take note of those that do not refer exclusively to string match
#      instances
#NOTE is there anything to be said about common nouns that are:
#      *coreferent with a proper name? 
#      *in a chain with real pronouns?
ACE=False
PRONOUNS=False
VERBOSE=False
USE_GOLD=False
TRUE_PRONOUNS = ("he", "she", "her", "him", "they", "them", "it")

#unannotated criteria
COUNT_CUTOFF = 5     #probably should be 10%? of the documents
DOC_CUTOFF   = 2     #probably should be 5%? of the documents
DOC_FREQ     = 2.0   #?
FOCUS        = 0.5   #the antecedent is a subj or dobj over half the time
HIGH_MOD     = 0.33  #modified more often
#annotated criteria
COVERAGE     = 0.25  #chain covers 25% of doc
SENT_DIST_3  = 0.75  #75% of antecedents are within 3 sentences
STARTS_CHAIN = 0.25  #this word starts chains very infrequently
#wn criteria
HIGH_CHILD   = 0.33  #wn children
LOW_RANK     = 0.5   #low hierarchical rank

#NOTE: the following criteria are not currently used
POSS         = 0.33  #possessor
BARE_DEF     = 0.25  #bare definite

def process_syntax(f, np, head, text, head2qp, stanford_deps):
    #TODO check for cases where dep_key isn't found might be an error in
    #finding the head bytespan
    dep_key = "{0},{1}".format(np["HEAD_START"], np["HEAD_END"])
    pos_tags = reconcile.getPOS(f)

    already_subj_this_time = False
    already_dobj_this_time = False
    already_iobj_this_time = False
    already_bd_this_time = False
    already_appos_this_time = False
    already_appos_this_time2 = True
    already_modded_once = False
    already_poss_once = False
    already_of_once = False
    for dep in stanford_deps:
        if (dep["RELATION"] == "nsubj" or dep["RELATION"] == "nsubjpass") \
                and dep_key == dep["DEP_SPAN"] and not already_subj_this_time:
            #we have a subj
            head2qp[head].subj += 1
            already_subj_this_time = True

        if dep["RELATION"] == "dobj" and dep_key == dep["DEP_SPAN"] and not already_dobj_this_time:
            #direct obj
            head2qp[head].dobj += 1
            already_dobj_this_time = True

        if dep["RELATION"] == "iobj" and dep_key == dep["DEP_SPAN"] and not already_iobj_this_time:
            #indirect object
            head2qp[head].iobj += 1
            already_iobj_this_time = True

        #apposition
        if dep["RELATION"] == "appos":
            if dep_key == dep["DEP_SPAN"]:
                head2qp[head].appos_dep += 1
                already_appos_this_time = True
            elif dep_key == dep["GOV_SPAN"]:
                head2qp[head].appos_gov += 1
                already_appos_this_time2 = True

        if dep["RELATION"] == "agent":
            if dep_key == dep["DEP_SPAN"]:
                head2qp[head].agent += 1
                head2qp[head].agent_verbs.append(dep["GOV"])

        if dep["RELATION"] == "amod":
            if dep_key == dep["GOV_SPAN"]:
                head2qp[head].adj_mod += 1
                #already_modded_once = True

        if dep["RELATION"] == "advmod":
            if dep_key == dep["GOV_SPAN"]:
                head2qp[head].adv_mod += 1
                #already_modded_once = True

        if dep["RELATION"] == "nn":
            if dep_key == dep["GOV_SPAN"]:
                head2qp[head].nn_mod += 1
                already_modded_once = True

                dep_start = int(dep["DEP_SPAN"].split(",")[0])
                dep_end = int(dep["DEP_SPAN"].split(",")[1])

                tag = pos_tags.getAnnotBySpan(dep_start, dep_end)
                if tag is not None:
                    if tag["TAG"] in ("NNP", "NNPS"):
                        head2qp[head].prp_mod += 1
                    elif tag["TAG"] in ("NN", "NNS"):
                        head2qp[head].nom_mod += 1

        if dep["RELATION"] == "num":
            if dep_key == dep["GOV_SPAN"]:
                head2qp[head].num_mod += 1
                already_modded_once = True

        if dep["RELATION"] == "poss":
            #the possessed
            if dep_key == dep["GOV_SPAN"] and not already_poss_once:
                head2qp[head].poss_mod += 1
                already_poss_once = True
                already_modded_once = True
            elif dep_key == dep["DEP_SPAN"]:
                #the possessor
                head2qp[head].is_poss += 1

        #NOTE prep_ can appear more than once for a single noun, which throws
        #off percentages
        if dep["RELATION"] in ("prep_of") and not already_of_once:
            if dep_key == dep["GOV_SPAN"]:
                head2qp[head].prep_mod += 1
                already_of_once = True

        if dep["RELATION"] in ("rcmod"):
            if dep_key == dep["GOV_SPAN"]:
                head2qp[head].rc_mod += 1

    if already_modded_once:
        head2qp[head].one_premod += 1

    #NOTE: modification levels should be low
    if (text == "the " + head) or \
            (text == "that " + head) or \
            (text == "this " + head) or \
            (text == "those " + head) or \
            (text == "these " + head):
        if not already_bd_this_time:
            head2qp[head].bare_definite += 1
            already_bd_this_time = True

    if (text.startswith("the ")):
        head2qp[head].definite += 1
    if (text.startswith("a ") or text.startswith("an ")):
        head2qp[head].indefinite += 1
        if already_appos_this_time or already_appos_this_time2:
            head2qp[head].ind_no_app += 1

def process(f, head2qp, annotated_file):
    stanford_deps = reconcile.getStanfordDep(f)
    pos = reconcile.getPOS(f)
    if annotated_file:
        nps = reconcile.getNPs(f)
        for np in nps:
            head = None
            text = None
            if PRONOUNS:
                if qp_utils.isPronoun(np):
                    head = np.getText().lower()
                    text = np.getText()
                else:
                    continue
            else:
                if qp_utils.isNominal(np, pos):
                    text = utils.textClean(np.getText())
                    np_tags = pos.getSubset(np.getStart(), np.getEnd())
                    head = utils.textClean(qp_utils.getHead2(text.lower(), np_tags))
                else:
                    continue

            #bookkeeping
            if head not in head2qp.keys():
                head2qp[head] = QuasiPronoun(head)
                head2qp[head].updateCount(True)
                head2qp[head].updateDocs(f, True)
            else:
                head2qp[head].updateDocs(f, True)
                head2qp[head].updateCount(True)

            if USE_GOLD:
                gold_chains = reconcile.getGoldChains(f)
                process_gold(f, np, head, text, head2qp, gold_chains)
            process_syntax(f, np, head, text, head2qp, stanford_deps)
    else:
        stanford_nps = reconcile.getStanfordNPs(f)
        for np in stanford_nps:
            if PRONOUNS:
                if np["is_pronoun"]:
                    head = np.getText().lower()
                    text = np.getText()
                else:
                    continue
            else:
                #skip some problems with the parser or numbers
                if np["HEAD"].startswith("$") or np["HEAD"].endswith("%") or np["HEAD"] == ".":
                    continue

                if np["is_nominal"]:
                    text = utils.textClean(np.getText())
                    head = np["HEAD"].lower()
                else:
                    continue

            #bookkeeping
            if head not in head2qp.keys():
                head2qp[head] = QuasiPronoun(head)
                head2qp[head].updateDocs(f, False)
                head2qp[head].updateCount(False)
            else:
                head2qp[head].updateDocs(f, False)
                head2qp[head].updateCount(False)
            process_syntax(f, np, head, text, head2qp, stanford_deps)

def processACE(f, head2qp):
    global USE_GOLD
    ace_annots = reconcile.parseGoldAnnots(f)
    nps = reconcile.getNPs(f)
    stanford_deps = reconcile.getStanfordDep(f)
    gold_chains = reconcile.getGoldChains(f)
    for np in nps:
        ace_np = ace_annots.getAnnotBySpan(np.getStart(), np.getEnd())
        head = None
        text = None
        if PRONOUNS:
            if qp_utils.isPronoun(np):
                head = ace_np["HEAD"].lower()
                text = np.getText()
            else:
                continue
        else:
            if ace_np["is_nominal"]:
                head = utils.textClean(ace_np["HEAD"].strip().lower())
                text = utils.textClean(np.getText())
            else:
                continue

        #bookkeeping
        if head not in head2qp.keys():
            head2qp[head] = QuasiPronoun(head)
        else:
            head2qp[head].updateDocs(f)
            head2qp[head].updateCount()

        if ace_np["GOLD_SINGLETON"]:
            head2qp[head].singleton += 1
            if (text.startswith("a ") or text.startswith("an ")):
                head2qp[head].faux_ba += 1
        else:
            #does it start the chain?
            if USE_GOLD:
                process_gold(f, np, head, text, head2qp, gold_chains)
        process_syntax(f, np, head, text, head2qp, stanford_deps)

def process_gold(f, np, head, text, head2qp, gold_chains):
    #find the chain of this np
    np_chain = None
    for chain in gold_chains.keys():
        for mention in gold_chains[chain]:
            if np == mention:
                np_chain = gold_chains[chain]
                break

    #find closest antecedent
    prev = None
    for other in np_chain:
        if np == other:
            break
        else:
            prev = other

    sentences = reconcile.getSentences(f)
    if prev is not None:
        head2qp[head].has_antecedent += 1
        i=0
        anaphor_sent = 0
        antecedent_sent = 0
        #find sentence distance
        for sent in sentences:
            if sent.contains(np):
                anaphor_sent = i
            if sent.contains(prev):
                antecedent_sent = i
            i+=1
        sentence_distance = abs(anaphor_sent - antecedent_sent)
        #how many antecedents within three sentences of antecedent
        head2qp[head].sent_distances.append(sentence_distance)

    #if it is a bare definite, how many are base antecedents?
    if (text == "the " + head) or \
            (text == "that " + head) or \
            (text == "this " + head) or \
            (text == "those " + head) or \
            (text == "these " + head):
        if np_chain[0] == np:
            head2qp[head].bdef_starts_chain += 1
    else:
        if np_chain[0] == np:
            head2qp[head].starts_chain += 1
            #is this is indef ba? how well does this track with the total % of
            #indefs?
            if (text.startswith("a ") or text.startswith("an ")):
                head2qp[head].faux_ba += 1

    #TODO how many string matches?
    #TODO how many proper names?
    #TODO diversity of antecedents

    #chain coverage in document [% of document sentences chain touches]
    covered_sentences = range(len(sentences))
    i = 0
    for sent in sentences:
        for mention in np_chain:
            if sent.contains(mention):
                covered_sentences.remove(i)
                break
        i+=1
    chain_coverage = float(len(sentences) - len(covered_sentences)) / len(sentences)
    head2qp[head].chain_coverage[f] = chain_coverage

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--annotated-filelist", dest="annotated_filelist",
            help="A list of annotated files to process", type="string",
            action="store", default=None)
    parser.add_option("-u", "--unannotated-filelist", dest="unannotated_filelist",
            help="A list of unannotated files to process", type="string",
            action="store", default=None)
    parser.add_option("-l", "--wn-labels", dest="wn_labels",
            help="File containing wordnet specificity labels", type="string",
            action="store", default=None)
    parser.add_option("-d", "--dataset", dest="dataset",
            help="The dataset's name", type="string",
            action="store", default=None)
    parser.add_option("-v", help="Verbosity", action="store_true",
            dest="verbose", default=False)
    parser.add_option("-p", help="Generate stats for true pronouns only", action="store_true",
            dest="pronouns", default=False)
    parser.add_option("-g", help="Generate stats with gold data", action="store_true",
            dest="use_gold", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    if options.verbose:
        VERBOSE=True
    if options.pronouns:
        PRONOUNS=True
    if options.use_gold or options.wn_labels is not None:
        USE_GOLD=True
    if options.dataset.find("ACE") > -1:
        ACE=True

    #read in the annotated files to process
    annotated_files = []
    with open(options.annotated_filelist, 'r') as fileList:
        annotated_files.extend(filter(lambda x : not x.startswith("#"),
            fileList.readlines()))

    unannotated_files = []
    if options.unannotated_filelist is not None:
        with open(options.unannotated_filelist, 'r') as fileList:
            unannotated_files.extend(filter(lambda x : not x.startswith("#"),
                fileList.readlines()))

    i=0
    files = annotated_files + unannotated_files
    prog = ProgressBar(len(files))
    head2qp = {}
    qp_utils.set_dataset(options.dataset)
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        prog.update_time(i)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        i += 1

        if ACE:
            processACE(f,head2qp)
        else:
            if f+"\n" in annotated_files:
                process(f, head2qp, True)
            else:
                process(f, head2qp, False)
    sys.stderr.write("\r \r\n")

    if options.wn_labels is not None:
        with open(options.wn_labels, 'r') as wnLabels:
            first = True
            for line in wnLabels:
                if line.startswith("#"):continue
                line = line.strip()
                if first:
                    first = False
                    continue
                tokens = line.split()
                word = tokens[-1].strip()
                if word not in head2qp.keys():
                    continue
                children = float(tokens[3])
                depth = float(tokens[6])
                head2qp[word].h_depth = depth
                head2qp[word].wn_children = children

    sorted_qps = sorted(head2qp.values(), key=lambda x : x.totalCount(), reverse=True)
    if not USE_GOLD:
        print "{0:4} {1:3} {2:>4} {3:>4} {4:>4} {5}".format(
                "cou",  #0
                "doc",  #1
                "foc",  #2
                "ind",  #3
                "amd",  #4
                "head"  #5
                )

        for n in sorted_qps:
            #has to have appeared more than 5 times and in at least 3 docs
            if n.totalCount() >= COUNT_CUTOFF and n.totalDocs() >= DOC_CUTOFF:
                pmd = float(n.one_premod)/n.totalCount()
                rmd = float(n.prep_mod+n.rc_mod)/n.totalCount()
                amd = pmd+rmd

                #TODO think of a better way to do this
                if amd > 1.0:
                    amd = 1.0

                print "{0:4} {1:3} {2:0.2f} {3:0.2f} {4:0.2f} {5}".format(
                        n.totalCount(),                      #0
                        n.totalDocs(),                       #1
                        float(n.subj+n.dobj)/n.totalCount(), #2
                        float(n.ind_no_app)/n.totalCount(),  #3
                        amd,                                 #4
                        n.head                               #5
                        )

    elif options.wn_labels is not None:
        print "{0:>4} {1:>3} {2:>4} {3:>4} {4:>4} {5:>4} {6:>4} {7:>4} {8:>4} {9:>4} {10:>4} {11}".format(
                "cou",  #0
                "doc",  #1
                "foc",  #2
                "ind",  #3
                "amd",  #4
                "<3s",  #5 gold data required
                "noa",  #6 gold data required
                "cdc",  #7 gold data required
                "dep",  #8 wordnet labels required
                "chi",  #9 wordnet labels required
                "qp?",  #10 label
                "head"  #11
                )

        final_qps = []
        for n in sorted_qps:
            pro_count = 0
            #has to have appeared more than 5 times and in at least 3 docs
            if (n.totalCount() >= COUNT_CUTOFF) and (n.totalDocs() >= DOC_CUTOFF):

                #measure the criteria
                if n.less_than_three() >= SENT_DIST_3:
                    pro_count += 1

                focus = float(n.subj+n.dobj)/n.totalCount()
                if focus >= FOCUS:
                    pro_count += 1

                #poss = float(n.poss_mod+n.is_poss)/n.totalCount()
                #if poss >= POSS:
                #    pro_count += 1
                ind_no_app = float(n.ind_no_app)/n.totalCount()

                try:
                    ba = float(n.singleton+n.starts_chain) / n.annotated_count
                except:
                    ba = 0.0

                if ba <= STARTS_CHAIN:
                    pro_count += 1

                #bdf = float(n.bare_definite)/n.totalCount()
                #if bdf >= BARE_DEF:
                #    pro_count += 1

                pmd = float(n.one_premod)/n.totalCount()
                rmd = float(n.prep_mod+n.rc_mod)/n.totalCount()
                amd = pmd+rmd
                if amd > 1.0:
                    amd = 1.0

                if amd >= HIGH_MOD:
                    pro_count += 1

                if n.h_depth <= LOW_RANK:
                    pro_count += 1

                if n.wn_children >= HIGH_CHILD:
                    pro_count += 1

                try:
                    chain_coverage = float(sum(n.chain_coverage.values())) / len(n.annotated_docs.keys())
                except:
                    chain_coverage = 0.0

                if chain_coverage >= COVERAGE:
                    pro_count += 1

                if pro_count >= 4:
                    final_qps.append(n.head)

                label = "{0}".format(pro_count)
                print "{0:>4} {1:>3} {2:>4.2f} {3:>4.2f} {4:>4.2f} {5:>4.2f} {6:>4.2f} {7:>4.2f} {8:>4.2f} {9:>4.2f} {10:>4} {11}".format(
                        n.totalCount(),                      #0
                        n.totalDocs(),                       #1
                        focus,                               #2
                        ind_no_app,                          #3
                        amd,                                 #4
                        n.less_than_three(),                 #5
                        ba,                                  #6
                        chain_coverage,                      #7
                        n.h_depth,                           #8
                        n.wn_children,                       #9
                        label,                               #10
                        n.head                               #11
                        )

            with open("{0}.qps".format(options.dataset), 'w') as outFile:
                st = datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y %H:%M:%S')
                outFile.write("# {0} QPs generated {1}\n".format(options.dataset, st))
                for word in final_qps:
                    outFile.write("{0}\n".format(word))
    else:
        print "{0:4} {1:3} {2:>4} {3:>4} {4:>4} {5:>4} {6:>4} {7:>4} {8:>4} {9}".format(
                "cou",  #0
                "doc",  #1
                "foc",  #2
                "pmd",  #3
                "rmd",  #4
                "bds",  #5 gold data required
                "cdc",  #6 gold data required
                "<3s",  #7 gold data required
                "noa",  #8 gold data required
                "head"  #9 gold data required
                )

        for n in sorted_qps:
            #has to have appeared more than 5 times and in at least 3 docs
            if n.totalCount() >= COUNT_CUTOFF and n.totalDocs() >= DOC_CUTOFF:
                print "{0:4} {1:3} {2:0.2f} {3:0.2f} {4:0.2f} {5:0.2f} {6:0.2f} {7:0.2f} {8:0.2f} {9}".format(
                        n.totalCount(),                                                    #0
                        n.totalDocs(),                                                     #1
                        float(n.subj+n.dobj)/n.totalCount(),                               #2
                        float(n.one_premod)/n.totalCount(),                                #3
                        float(n.prep_mod+n.rc_mod)/n.totalCount(),                         #4
                        float(n.bdef_starts_chain)/n.totalCount(),                         #5
                        float(sum(n.chain_coverage.values()))/len(n.annotated_docs.keys()),#6
                        n.less_than_three(),                                               #7
                        float(n.singleton+n.starts_chain) / n.totalCount(),                #8
                        n.head                                                             #9
                        )
