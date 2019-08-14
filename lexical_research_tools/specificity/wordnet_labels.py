#!/usr/bin/python
# File Name : wordnet_labels.py
# Purpose : Labels NPs in a document with wordnet-based specificity rankings.
#           Take 2
# Creation Date : 08-01-2013
# Last Modified : Mon 16 Dec 2013 01:45:08 PM MST
# Created By : Nathan Gilbert
#
import sys
import operator

from pyconcile import reconcile
from pyconcile import utils
from pyconcile import data
from pyconcile.annotation_set import AnnotationSet

import specificity_utils
import en
from nltk.corpus import wordnet as wn

def ultimate_wordnet_specificity(head_synset):
    distance = head_synset.shortest_path_distance(wn.synset("entity.n.01"))
    return str(distance)

def wordnet_specificity(head_synset, sem_class):
    #iterate over wordnet and capture the top level synsets
    #for synset in list(wn.all_synsets('n')):
    #    print synset

    if head_synset is None or sem_class is None:
        return None

    other = None
    if sem_class == "PERSON":
        other = wn.synset('person.n.01')
    elif sem_class == "ANIMAL":
        other = wn.sysnet('animal.n.01')
    elif sem_class == "PLANT":
        other = wn.synset('plant.n.01')
    elif sem_class == "LOCATION" or sem_class == "GPE":
        other = wn.synset('location.n.01')
    elif sem_class.startswith("ORG"):
        #other = wn.synset('organization.n.01')
        other = wn.synset('group.n.01')
    elif sem_class == "BUILDING":
        other = wn.synset('building.n.01')
    elif sem_class == "DISEASE":
        other = wn.synset('illness.n.01')
    elif sem_class == "EVENT":
        other = wn.synset('event.n.01')
    elif sem_class == "VEHICLE":
        other = wn.synset('vehicle.n.01')
    elif sem_class == "NUMBER":
        other = wn.synset('number.n.01')
    elif sem_class == "ABSTRACT":
        other = wn.synset('abstraction.n.01')
    elif sem_class == "PHYS-OBJ":
        other = wn.synset('object.n.01')
    else:
        other = None

    if other is None:
        return None

    #2. get the depth from entity and the SCI synset
    distance = head_synset.shortest_path_distance(other)
    return str(distance)
    #print distance
    #if distance < CUTOFF:
    #    return "Identifier"
    #else:
    #    return "Descriptor"
    #if wn.synset(head_synset.name).min_depth() < CUTOFF:
    #3. the number of senses per word (more senses, more general)
    #4. some mixture of the depth and # of senses

def wordnet_semantic_type(hypernyms):

    for hyper in hypernyms:
        for h in hyper:
            if h.upper() == "MAN" or h.upper() == "WORKER" or h.upper() == "PEOPLE":
                return "PERSON"
            elif h.upper() == "ORGANIZATION" or\
                 h.upper() == "TEAM":
                return "ORG"
            elif h.upper() == "PERIOD OF TIME":
                return "DATE/TIME"
            elif h.upper() == "INTEGER" or\
                 h.upper() == "FRACTION" or\
                 h.upper() == "QUANTITY" or\
                 h.upper() == "NUMBER":
                return "NUMBER"
            elif h.upper() == "ABSTRACTION" or h.upper() == "ABSTRACT ENTITY":
                return "ABSTRACT"
            elif h.upper() == "PHYSICAL OBJECT" or\
                    h.upper() == "DOCUMENT" or\
                    h.upper() == "ARTIFACT" or\
                    h.upper() == "EQUIPMENT" or\
                    h.upper() == "OBJECT":
                return "PHYS-OBJ"
            elif h.upper() == "GEOGRAPHIC AREA" or\
                    h.upper() == "REGION" or\
                    h.upper() == "ZONE" or\
                    h.upper() == "LANDMASS":
                return "LOCATION"
            elif h.upper() == "HUMAN ACTION" or\
                    h.upper() == "OCCURRENCE" or\
                    h.upper() == "SOCIAL EVENT" or\
                    h.upper() == "PROCESS" or\
                    h.upper() == "ACTION" or\
                    h.upper() == "GROUP ACTION":
                return "EVENT"
    return None

def sundance_semantic_type(head_span, sundance_nes):
    for ne in sundance_nes:
        if (head_span[0] >= ne.getStart()) and (head_span[1] <= ne.getEnd()):
            for sun in ne["SUN_NE"]:
                if sun.find("ORG") > -1:
                    return "ORG"
                elif sun.find("DISEASE") > -1 or sun.find("VIRUS") > -1 or sun.find("BACTERIUM") > -1:
                    return "DISEASE"
                elif sun.find("COUNTRY") > -1 \
                        or sun.find("LOCATION") > -1 \
                        or sun.find("BUILDING") > -1 \
                        or sun.find("PROVINCE") > -1 \
                        or sun.find("STATE") > -1 \
                        or sun.find("SITE") > -1:
                    return "LOCATION"
                elif sun.find("CIVILIAN") > -1 \
                    or sun.find("OFFICIAL") > -1 \
                    or sun.find("HUMAN") > -1:
                    return "PERSON"
                elif sun.find("PHYS") > -1 or sun.find("DOCUMENT") > -1 or sun.find("ANATOMY") > -1 or sun.find("FOOD") > -1 :
                    return "PHYS-OBJ"
                elif sun.find("PLANT") > -1:
                    return "PLANT"
                elif sun.find("MILITARY") > -1:
                    return "ORG"
                elif sun.find("EVENT") > -1 \
                        or sun.find("ATTACK") > -1:
                    return "EVENT"
                elif sun.find("TIME") > -1 \
                        or sun.find("YEAR") > -1 \
                        or sun.find("MONTH") > -1:
                    return "DATE/TIME"
                elif sun.find("ANIMAL") > -1 \
                        or sun.find("FISH") > -1 \
                        or sun.find("MAMMAL") > -1 \
                        or sun.find("BIRD") > -1:
                    return "ANIMAL"
    return None

def stanford_semantic_type(head_span, stanford_nes):
    for ne in stanford_nes:
        #print "NE: {0},{1}".format(ne.getStart(), ne.getEnd())
        if (head_span[0] >= ne.getStart()) and (head_span[1] <= ne.getEnd()):
            if ne["NE_CLASS"] == "ORGANIZATION":
                return "ORG"
            else:
                return ne["NE_CLASS"]
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist>" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    master_unknown_labels = 0
    master_unknown_sc     = 0
    master_total_nps      = 0

    no_semantics_noun_counts = {}
    no_label_noun_counts    = {}

    for f in files:
        f=f.strip()
        print("Document: {0}".format(f))

        #NOTE: assumes that the nps file will only have gold_nps in it.
        nps = reconcile.getNPs(f)
        gold_nps = reconcile.parseGoldAnnots(f)
        gold_nes = reconcile.getGoldNEs(f)
        common_nouns = AnnotationSet("common_nouns")
        rawText = ""
        with open(f+"/raw.txt", 'r') as txtFile:
            rawText = ''.join(txtFile.readlines())

        for np in nps:
            gold_np = gold_nps.getAnnotBySpan(np.getStart(), np.getEnd())
            if not gold_np["GOLD_SINGLETON"] and gold_np["is_nominal"]:
                np["HEAD"] = rawText[gold_np["HEAD_START"]:gold_np["HEAD_END"]]
                np["HEAD_START"] = gold_np["HEAD_START"]
                np["HEAD_END"] = gold_np["HEAD_END"]
                common_nouns.add(np)

        labels = {}
        noun_class = {}
        sundance_nes = reconcile.getSundanceNEs(f)
        stanford_nes = reconcile.getNEs(f)

        for np in common_nouns:
            #print np.ppprint()
            key = "{0}:{1}".format(np.getStart(),np.getEnd())

            #may need to get head for a lot of NPs.
            text = utils.textClean(np.getText().lower())
            if np["HEAD"] is not None:
                head = np["HEAD"]
                head_span = (np["HEAD_START"], np["HEAD_END"])
            else:
                head = specificity_utils.getHead(text)
                head_span = specificity_utils.getHeadSpan(np, head)

            if head_span is not None:
                #print "{0} : {1}".format(rawText[head_span[0]:head_span[1]],
                #        head_span)
                stanford_cls = stanford_semantic_type(head_span, stanford_nes)
                sundance_cls = sundance_semantic_type(head_span, sundance_nes)

            #is it a date or time?
            if np["DATE"] != "NONE" or utils.isDate(utils.textClean(np.getText())):
                noun_class[key] = "DATE/TIME"

            head_synset = None
            if key not in list(labels.keys()):
                hypernyms = en.noun.hypernyms(head, sense=0)
                synsets = wn.synsets(head)
                if len(hypernyms) < 1:
                    singular_head = en.noun.singular(head)
                    hypernyms = en.noun.hypernyms(singular_head, sense=0)
                    synsets = wn.synsets(singular_head)

                wordnet_cls = wordnet_semantic_type(hypernyms)
                if len(synsets) > 0:
                    head_synset = synsets[0]

            gold_ne = gold_nes.getAnnotBySpan(np.getStart(),
                    np.getEnd())
            if gold_ne is not None:
                noun_class[key] = gold_ne["NE_CLASS"]
            else:
                #try wordnet sem class
                if wordnet_cls is not None:
                    noun_class[key] = wordnet_cls
                else:
                    if sundance_cls is not None:
                        noun_class[key] = sundance_cls
                    else:
                        if stanford_cls is not None:
                            noun_class[key] = stanford_cls

            #try to use wordnet to get a specificity label
            wordnet_spec_label = wordnet_specificity(head_synset, noun_class.get(key, None))
            if wordnet_spec_label is not None:
                labels[key] = wordnet_spec_label

        #total_unknown_labels = 0
        #total_unknown_sc     = 0
        #for np in common_nouns:
            #key="{0}:{1}".format(np.getStart(),np.getEnd())
            ##print "{0:10} {1:15} {2}".format(labels.get(key, "?"),
            ##        noun_class.get(key, "?"), np.pprint().strip())
            #if labels.get(key, "?") == "?":
                #total_unknown_labels += 1
            #if noun_class.get(key, "?") == "?":
                #total_unknown_sc += 1

            #text = utils.textClean(np.getText().lower())
            #head = specificity_utils.getHead(text)
            #if labels.get(key, "?") == "?":
                #no_label_noun_counts[head] = no_label_noun_counts.get(head, 0) + 1
            #if noun_class.get(key, "?") == "?":
                #no_semantics_noun_counts[head] = no_semantics_noun_counts.get(head, 0) + 1

        #master_unknown_labels += total_unknown_labels
        #master_unknown_sc     += total_unknown_sc
        #print "="*40

        #output to file
        with open(f+"/annotations/wn_specificity_annots", 'w') as outFile:
            i = 0
            for np in common_nouns:
                key="{0}:{1}".format(np.getStart(),np.getEnd())
                text = utils.textClean(np.getText())
                if np["HEAD"] is not None:
                    head = np["HEAD"]
                else:
                    head = specificity_utils.getHead(text.lower())
                outFile.write("{0}\t{1},{2}\tSpecificity=\"{3}\"\tSemantic=\"{4}\"\tText=\"{5}\"\tHead=\"{6}\"\n".format(i, np.getStart(),
                    np.getEnd(), labels.get(key, "None"),
                    noun_class.get(key, "None"), text, head))
                i+=1
        master_total_nps += len(gold_nps)

    #sorted_no_labels = sorted(no_label_noun_counts.iteritems(),
    #        key=operator.itemgetter(1), reverse=True)

    #print "Most common unlabeled heads"
    #i = 0
    #for pair in sorted_no_labels:
    #    if i > 9:
    #        break
    #    print "{0:50} : {1:19}".format(pair[0], pair[1])
    #    i += 1
    #print "="*40

    #sorted_no_semantics = sorted(no_semantics_noun_counts.iteritems(),
    #        key=operator.itemgetter(1), reverse=True)
    #print "Most common heads without semantics"
    #i = 0
    #for pair in sorted_no_semantics:
    #    if i > 9:
    #        break
    #    print "{0:50} => {1:19}".format(pair[0], pair[1])
    #    i += 1
    #print "="*40
    #print "Unknown Labels: {0}/{1} = {2:0.2f}".format(master_unknown_labels, master_total_nps, float(master_unknown_labels)/master_total_nps)
    #print "Unknown SC:     {0}/{1} = {2:0.2f}".format(master_unknown_sc, master_total_nps, float(master_unknown_sc)/master_total_nps)


