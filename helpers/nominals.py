#!/usr/bin/python
# File Name : nominals.py
# Purpose : Created a db of nominals that are coreferent or not
# Creation Date : 07-07-2011
# Last Modified : Wed 13 Jul 2011 01:38:48 PM MDT
# Created By : Nathan Gilbert
#
import sys

from collections import defaultdict
from operator import itemgetter

from pyconcile import reconcile
from pyconcile import annotation_set
from pyconcile import utils
from pyconcile import entity

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s filelist" % (sys.argv[0]))
        sys.exit(1)

    fileList = open(sys.argv[1], 'r')
    anaphoric_nominals = annotation_set.AnnotationSet("anaphoric_noms")
    existential_nominals = annotation_set.AnnotationSet("exist_noms")
    
    for f in fileList:
        f = f.strip()
        if f.startswith("#"):
            continue
        
        print("Working on %s" % f)

        gold_annots = reconcile.parseGoldAnnots(f)
        gold_chains = reconcile.getGoldChains(f)
        
        response_nps = reconcile.getNPs_annots(f)
        pos = reconcile.getPOS(f, True)
        reconcile.addSundanceProps(f, response_nps)
        utils.match_nps(gold_annots, response_nps)

        for g in gold_annots:
            if g.getATTR("GOLD_TYPE") != "NOM":
                continue
            
            for r in response_nps:
                if g.getATTR("MATCHED") == r.getID():
                    g.addProps(r.getProps())
            
            if g.getATTR("GRAMMAR") == "SUBJECT" or g.getATTR("SUN_ROLE") == "SUBJ":
                g.setProp("S_VERB", reconcile.getSubjVerb(g, pos))        

            if g.getATTR("GRAMMAR") == "OBJECT" or g.getATTR("SUN_ROLE") == "DOBJ":
                g.setProp("O_VERB", reconcile.getObjVerb(g, pos)) 
                
            prev_ant = reconcile.getPreviousAntecedent(g, gold_chains)  
            if prev_ant.getText() != "":
                g.setProp("PREV_ANT", prev_ant.getText())     
                
            prev_proper_ant = reconcile.getPreviousProperAntecedent(g, gold_chains)
            if prev_proper_ant.getText() != "":
                g.setProp("PREV_PROP_ANT", prev_proper_ant.getText())

            if g.getATTR("GOLD_SINGLETON"):
                existential_nominals.add(g)
            else:
                anaphoric_nominals.add(g)

    #entities = []
    #for a in anaphoric_nominals:
    #    if a.getATTR("GOLD_TYPE") == "NOM":
    #        for e in entities:
    #            if e.getName() == a.getATTR("HEAD"):
    #                e.addAnnot(a)
    #                break
    #        else:
    #            new_ent = entity.Entity(a.getATTR("HEAD"))
    #            new_ent.addAnnot(a)
    #            entities.append(new_ent)

    ana_ent = defaultdict(list)
    ana_head_counts = {}

    for a in anaphoric_nominals:
        head = a.getATTR("HEAD")
        ana_ent[head].append(a)
        ana_head_counts[head] = ana_head_counts.get(head, 0) + 1
    
    heads_sorted = sorted(iter(ana_head_counts.items()), key=itemgetter(1), reverse=True)
    
    x = 0 
    for h in heads_sorted:
        if x > 25:
            break
        head = h[0]
        print()
        print("Nominal: %s" % head)
        output = ""
        output += "Count: %d" % ana_head_counts[head]
        s_verbs = "SUBJ:"
        o_verbs = "DOBJ:"
        modifiers = "MODS:"
#        semantic = "SEM:"
        
        for mention in ana_ent[head]:
#            semantic += " " + mention.getATTR("SEMANTIC")
            sv = mention.getATTR("S_VERB")
            ov = mention.getATTR("O_VERB")
            if sv != "":
                s_verbs += sv + ", "
                
            if ov != "":
                o_verbs += ov + ", "
        
            mds = mention.getATTR("MODIFIER")
            if mds != "":
                modifiers += mds + " "
#        output += "\n\t" + semantic 
        if s_verbs != "SUBJ:":    
            s_verbs = s_verbs.strip()[:-1]
            output += "\n\t" + s_verbs
        if o_verbs != "DOBJ:":
            o_verbs = o_verbs.strip()[:-1]
            output += "\n\t" + o_verbs
        if modifiers != "MODS:":
            output += "\n\t" + modifiers
            
        print(output)
        x += 1
