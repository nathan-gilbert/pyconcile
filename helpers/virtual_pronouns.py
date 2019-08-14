#!/usr/bin/python
# File Name : virtual_pronouns.py
# Purpose : Produce statistics of virtual pronouns in a corpus
# Creation Date : 08-15-2011
# Last Modified : Mon 26 Sep 2011 04:52:40 PM MDT
# Created By : Nathan Gilbert
# DONE: 1. Get average distance from previous antecedent.
# DONE: 2. What does reconcile say is each of these vp's semantic class?
# DONE: 3. How many nominals appear in two different chains in the same doc?
#          A. Many, ACE2v1/43 is a good example.
# DONE: 4. What is the prob that a given nominal is coreferent to another
#          nominal? A proper name? a pronoun? (getting at specificity of
#          nominal.)
#       1b.Inherit the (wind)semantic class from any element in the chain that
#       has one, and check for any other previous semantic classes that are not
#       in the same chain as the given. (discourse focus)
#       1c.verb stats for nominals, what verbs are they the subject of? object
#       of? etc. 
# DONE: 2. Need to fix base antecedent record keeping, over counting
# TODO: 3. Unannotated stats (hypothetic antecedent perhaps?)
# TODO: 4. Clustering vps? (via nltk) <- doing this in another program.
# DONE: 5. Fix segmentation issues (why negative values?) -incorrect
#       conditional hehe
# DONE: 6. Gold semantic classes coupled with +sundance semantics, what do I do
#       with this?
# DONE: 7. Avg possible correct antecedents. Can look at more "possible"
#       antecedents, wrt number, gender, semantics, etc.
# DONE: 8. Verbs that these nominals are commonly role fillers with. <- use
#       this with unannotated texts.
# DONE: 9. Contexts windows (5 words ahead, 5 words behind) <- use this with
#       unannotated texts. <- doing this in another program.
# TODO: 10. Adding in nominals from the document that are not in the gold

# Notes:
# The file list needs to be a list of files with a G or U one each line
# indicating whether or not the file is to be processed as a gold or
# unannotated file. 
import sys
from collections import defaultdict
from optparse import OptionParser

from pyconcile import reconcile
from pyconcile.annotation import Annotation
from pyconcile.document import Document
from pyconcile.bar import ProgressBar

total_counts = {}
total_counts_heads = {}

virtual_pronouns = {}
virtual_pronoun_heads = {}

nominal_base_antecedent = {}                 # the number of times a given nominal appears as a
                                             # base antecedent.
distance_from_antecedent = defaultdict(list) # the distances from the previous
                                             # antecedent
reconcile_semantic_class = defaultdict(list) # what does reconcile say is the
                                             # semantic class of this mention?
docs_appeared = defaultdict(list)            # keeping track of which nominals
                                             # are in different chains in the same doc.

nominals2type = defaultdict(dict)            # nominal -> antecedent type
                                             # {nominal, pronoun, proper} -> counts

focus_shift = {}                             # TODO: nominal -> int, there is another
                                             # mention that shares the same semantic 
                                             # class as the given nominal between it and
                                             # it's closest antecedent.

focus_distance = defaultdict(list)           # the distance in text tiles. 

gold_semantic_class = defaultdict(list)      # the gold semantic class(es) for this
                                             # nominal.

sun_semantic_class = defaultdict(list)       # the semantic class sundance
                                             # selected.

number_gold_antecedents = defaultdict(list)  # the number of antecedents this
                                             # nominal has in a document.

subj_verbs = defaultdict(list)               # the collection of verbs this
                                             # nominal shares a subj role with.

obj_verbs = defaultdict(list)                # the collection of verbs this
                                             # nominal shares a dobj role with.
def add_reconcile_semantic_class(gold_chains, nes):
    for key in gold_chains.keys():
        for mention in gold_chains[key]:
            if nes.contains(mention):
                cls = nes.getAnnotBySpan(mention.getStart(), \
                        mention.getEnd()).getATTR("NE_CLASS")
                        #mention.getEnd()).getATTR("SUN_NE") #get the sundance
                                                            #assigned semantic class.
                mention.setProp("NE_CLASS", cls[0])
            else:
                mention.setProp("NE_CLASS", "None")

#TODO, Sundance mostly gives NE types to single token NPs, therefore a lot of
# things are being skipped. Really need to make this work with multi word NPs.
def add_sundance_nps(chains, sun_nps):
    """add in sundance info to the supplied chains."""

    for key in chains.keys():
        for mention in chains[key]:
            subset = sun_nps.getSubset(mention.getStart(), mention.getEnd())

            #get the role of the np
            if sun_nps.contains(mention):
                sun_np = sun_nps.getAnnotBySpan(mention.getStart(),
                        mention.getEnd())
                mention.setProp("ROLE", sun_np.getATTR("ROLE"))

            head = Annotation(mention.getATTR("HEAD_START"), \
                    mention.getATTR("HEAD_END"), 0, {}, \
                    mention.getATTR("HEAD_TEX"))

            if sun_nps.contains(head):
                sun_np = sun_nps.getAnnotBySpan(mention.getStart(),
                        mention.getEnd())
                mention.setProp("SUN_SEMANTIC", sun_np.getATTR("SEM"))

            #morphs=[]
            #roles=[]
            #sem=[]
            #for sun_np in subset:
            #    morphs.append(sun_np.getATTR("MORPH"))
                #roles.append(sun_np.getATTR("ROLE"))
            #    sem.append(sun_np.getATTR("SEM"))

            #mention.setProp("MORPH", morphs)
            #mention.setProp("ROLE", roles)
            #mention.setProp("SUN_SEMANTIC", sem)

def gold_annotations(f):
    """process the file with gold annotations"""

    global virtual_pronouns, total_counts, virtual_pronoun_heads, \
    nominal_base_antecedent, distance_from_antecedent

    doc = Document(f)
    gold_chains = reconcile.getGoldChains(f)

    #adding in Sundance nes.
    nes = reconcile.getNEs(f, True)
    add_reconcile_semantic_class(gold_chains, nes)

    #adding in Reconcile pos too.
    pos = reconcile.getPOS(f, True)

    #getting the docs nps
    reconcile_nps = reconcile.getNPs_annots(f)

    #getting sundance nps
    sundance_nps = reconcile.getSundanceNPs(f)
    add_sundance_nps(gold_chains, sundance_nps)

    original_text_heads = {}            # just getting the heads
    original_text = defaultdict(list)   # for getting total doc counts later.
    nominal2chains = defaultdict(list)  # the chains that a given nominal appears.

    for chain in gold_chains.keys():
        base_antecedent = True
        prev_annot = None
        antecedents = 0
        for mention in gold_chains[chain]:

            #if the first antecedent in a chain, do not list it as anaphoric.
            if base_antecedent:
                if mention.getATTR("is_nominal") and not \
                mention.getATTR("GOLD_SINGLETON"):
                    text = mention.getText()
                    text_lower = mention.getATTR("TEXT_CLEAN").lower()
                    docs_appeared[text_lower].append(f)

                    nominal_base_antecedent[text_lower] = \
                    nominal_base_antecedent.get(text_lower, 0) + 1

                    original_text[text_lower].append(text)

                    #take note that this chain contained this nominal
                    nominal2chains[text_lower].append(chain)

                    #take note of the gold semantic class
                    gold_semantic_class[text_lower].append(mention.getATTR("GOLD_SEMANTIC"))

                    #reconcile's semantic class
                    reconcile_semantic_class[text_lower].append(mention.getATTR("NE_CLASS"))

                    #sundance's semantic class
                    sun_semantic_class[text_lower].append(mention.getATTR("SUN_SEMANTIC"))

                    number_gold_antecedents[text_lower].append(antecedents)

                    #get verb stats
                    if mention.getATTR("ROLE") == "SUBJ":
                        verb = reconcile.getSubjVerb(mention, pos)
                        if verb != None:
                            subj_verbs[text_lower].append(verb.lower())
                    elif mention.getATTR("ROLE") == "DOBJ":
                        verb = reconcile.getObjVerb(mention, pos)
                        if verb != None:
                            obj_verbs[text_lower].append(verb.lower())

                base_antecedent = False
                prev_annot = mention
                antecedents += 1
                continue

            if mention.getATTR("is_nominal"):
                text = mention.getText()
                text_lower = mention.getATTR("TEXT_CLEAN").lower()
                head_text = mention.getATTR("HEAD_TEXT")

                original_text[text_lower].append(text)
                virtual_pronouns[text_lower] = \
                virtual_pronouns.get(text_lower, 0) + 1

                virtual_pronoun_heads[head_text.lower()] = \
                virtual_pronoun_heads.get(head_text.lower(), 0) + 1

                #the semantic class Reconcile puts this in.
                reconcile_semantic_class[text_lower].append(mention.getATTR("NE_CLASS"))

                #register this doc as containing this np.
                docs_appeared[text_lower].append(f)

                #take note that this chain contained this nominal
                nominal2chains[text_lower].append(chain)

                #take note of the gold semantic class
                gold_semantic_class[text_lower].append(mention.getATTR("GOLD_SEMANTIC"))

                #the number of possible correct antecedents for this anaphor
                number_gold_antecedents[text_lower].append(antecedents)

                #sundance's semantic class
                sun_semantic_class[text_lower].append(mention.getATTR("SUN_SEMANTIC"))

                # subject verb statistics
                if mention.getATTR("ROLE") == "SUBJ":
                    verb = reconcile.getSubjVerb(mention, pos)
                    subj_verbs[text_lower].append(verb.lower())
                elif mention.getATTR("ROLE") == "DOBJ":
                    verb = reconcile.getObjVerb(mention, pos)
                    obj_verbs[text_lower].append(verb.lower())

                #get the sentence distance from these two mentions.
                mention_sent = reconcile.getAnnotSentence(f, mention)
                prev_sent = reconcile.getAnnotSentence(f, prev_annot)

                if mention_sent > -1 and prev_sent > -1:
                    distance_from_antecedent[text_lower].append(mention_sent - \
                            prev_sent)

                #get the TextTiling segment distance for the two mentions
                mention_seg = doc.getAnnotTile(mention)
                prev_seg = doc.getAnnotTile(prev_annot)
                if mention_seg > -1 and prev_seg > -1:
                    focus_distance[text_lower].append(mention_seg - \
                            prev_seg)

                #getting the distribution of closest antecedent types for a 
                #given nominal
                if prev_annot.getATTR("is_nominal"):
                    nominals2type[text_lower]["nominal"] = \
                    nominals2type[text_lower].get("nominal",0) + 1
                elif prev_annot.getATTR("is_pronoun"):
                    nominals2type[text_lower]["pronoun"] = \
                    nominals2type[text_lower].get("pronoun",0) + 1
                else:
                    nominals2type[text_lower]["proper"] = \
                    nominals2type[text_lower].get("proper",0) + 1
            prev_annot = mention
            antecedents += 1

    #for key in nominal2chains.keys():
    #    print "%d : %s (doc: %s)" % (len(list(set(nominal2chains[key]))), key,
    #            doc)

    #update the total counts.
    for key in original_text.keys():
        for text in list(set(original_text[key])):
            total_counts[key] = total_counts.get(key, 0) + doc.getWordCounts(text)

    #the head counts
    for key in virtual_pronoun_heads.keys():
        total_counts_heads[key] = total_counts_heads.get(key, 0) + \
        doc.getWordCounts(key)

def no_annotations(f):
    """process the file with no annotations"""
    pass

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    #parser.add_option("-u", "--unannotated-only", help="Only collect stats on \
    #        unannotated documents.", action="store_true",
    #        dest="unannotated", default=False)
    #parser.add_option("-e", "--heads", help="Print heads only", action="store_true",
    #        dest="heads", default=False)
    parser.add_option("-v", "--verbose", help="Verbosity", action="store_true",
            dest="verbose", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    fileList = open(sys.argv[1], 'r')
    files = fileList.readlines()
    fileList.close()
    processed = 0
    for line in files:
        print line

        if options.verbose:
            prog = ProgressBar(len(files))
            sys.stdout.write("\r")
            prog.update_time(processed)
            sys.stdout.write("\r%s" % (str(prog)))
            sys.stdout.flush()

        tokens = line.split()
        t=tokens[0].strip()
        f=tokens[1].strip()

        if t == "G":
            gold_annotations(f)
        else:
            no_annotations(f)
        processed += 1

    if options.verbose:
        sys.stdout.write("\r \r\n")

    outFile = open("ace-stats", 'w')
    for key in virtual_pronouns.keys():
        #the average distance between mention and antecedent in sentences.
        try:
            avg_distance = \
            float(sum(distance_from_antecedent[key])) / \
            len(distance_from_antecedent[key])
        except ZeroDivisionError:
            avg_distance = 0.0

        #get average segment distance
        try:
            avg_seg_distance = \
                    float(sum(focus_distance[key])) / \
                    len(focus_distance[key])
            avg_seg_distance = abs(avg_seg_distance)
        except ZeroDivisionError:
            avg_seg_distance = 0.0

        #the avg # of possible antecedents
        avg_ants = float(sum(number_gold_antecedents[key])) / \
        len(number_gold_antecedents[key])

        #the probability that a nominal is a vp.
        prob_vp = float(virtual_pronouns[key]) / total_counts[key]

        #the probability that a nominal is a base antecedent.
        prob_ba = float(nominal_base_antecedent.get(key, 0.0))/total_counts[key]

        #the probability of being existential
        prob_exist =  1.0 - (prob_vp + prob_ba)

        #the set of semantic classes assigned to this nominal
        semantic_classes = ' '.join(list(set(reconcile_semantic_class[key])))

        #gold set of semantic classes
        gold_semantic_classes = ' '.join(list(set(gold_semantic_class[key])))

        #reconcile semantic class
        rec_semantic_classes = \
        ' '.join(list(set(reconcile_semantic_class[key])))

        sun_semantic_classes = \
        ' '.join(list(set(sun_semantic_class[key])))

        #the number of documents that this word appeared. 
        num_docs = len(list(set(docs_appeared[key])))

        #getting antecedent probs
        total_ants = nominals2type[key].get("nominal", 0) + \
        nominals2type[key].get("pronoun", 0) + \
        nominals2type[key].get("proper", 0)

        prob_ant_nominal = nominals2type[key].get("nominal", 0) / \
        float(total_ants)

        prob_ant_pronoun = nominals2type[key].get("pronoun", 0) / \
        float(total_ants)

        prob_ant_proper = nominals2type[key].get("proper", 0) / \
        float(total_ants)

        subj = list(set(subj_verbs[key]))
        obj  = list(set(obj_verbs[key]))

        outFile.write("%d : %s : %s : %s : %s : %s \n" % (total_counts[key], key, \
            gold_semantic_classes, subj, obj, sun_semantic_classes))

        #print "%3d : %3d : %3d : %1.2f : %1.2f : %1.2f : %3d : %1.2f : %1.2f : %1.2f : %1.2f : %1.2f : %1.2f : %s" % \
        print "%s : %3d : %3d : %3d : %1.2f : %1.2f : %1.2f : %3d : %1.2f : %1.2f : %1.2f : %1.2f : %1.2f : %1.2f" % \
            (key, \
            virtual_pronouns[key], \
            nominal_base_antecedent.get(key,0), \
            total_counts[key], \
            prob_vp, \
            prob_ba, \
            prob_exist, \
            num_docs, \
            #semantic_classes, \
            prob_ant_nominal, \
            prob_ant_pronoun, \
            prob_ant_proper,
            avg_distance, \
            avg_seg_distance,
            avg_ants
            #key
            )
    outFile.close()
