#!/usr/bin/python
# File Name : qp-finder.py
# Purpose : This is a script to hunt out the characteristics of common noun
# instances that are in close proximity to their antecedents.
# Creation Date : 12-12-2013
# Last Modified : Tue 17 Dec 2013 10:23:20 AM MST
# Created By : Nathan Gilbert
#
#TODO: need to extend this to perform as best as I can for MUC-6/MUC-7/Promed/MUC-4
#      really try to get the NP demarcations correct and the correct head
#      nouns.
#NOTE: What I really want to get at what are the combinations of these that are associated
#      with close proximity of their antecedents.
import sys

from pyconcile import reconcile
from pyconcile import utils
from pyconcile.bar import ProgressBar
from qp import QuasiPronoun

#TODO output in a format that will allow for cataloging experiments in a
#      manner discussed with Ellen.
#NOTE are there different words used when a noun is subjective/objective/possessive? [like for pronouns]

#TODO take note of those that do not refer exclusively to string match
#      instances
#TODO appear as subjects a lot [reminiscent of he/she]
#TODO appear close to their antecedents

#NOTE is there anything to be said about common nouns that are:
#      *coreferent with a proper name? 
#      *in a chain with real pronouns?
ACE=True
TRUE_PRONOUNS = ("he", "she", "her", "him", "they", "them", "it")

def process(f, np, head, text, heads2qp, stanford_deps):
    dep_key = "{0},{1}".format(np["HEAD_START"], np["HEAD_END"])
    pos_tags = reconcile.getPOS(f)
    for dep in stanford_deps:
        if (dep["RELATION"] == "nsubj" or dep["RELATION"] == "nsubjpass") and dep_key == dep["DEP_SPAN"]:
            #we have a subj
            heads2qp[head].subj += 1

        if dep["RELATION"] == "dobj" and dep_key == dep["DEP_SPAN"]:
            #direct obj
            heads2qp[head].dobj += 1

        if dep["RELATION"] == "iobj" and dep_key == dep["DEP_SPAN"]:
            #indirect object
            heads2qp[head].iobj += 1

        #apposition
        if dep["RELATION"] == "appos":
            if dep_key == dep["DEP_SPAN"]:
                heads2qp[head].appos_dep += 1
            elif dep_key == dep["GOV_SPAN"]:
                heads2qp[head].appos_gov += 1

        if dep["RELATION"] == "agent":
            if dep_key == dep["DEP_SPAN"]:
                heads2qp[head].agent += 1
                heads2qp[head].agent_verbs.append(dep["GOV"])

        if dep["RELATION"] == "amod":
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].adj_mod += 1

        if dep["RELATION"] == "advmod":
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].adv_mod += 1

        if dep["RELATION"] == "nn":
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].nn_mod += 1

                dep_start = int(dep["DEP_SPAN"].split(",")[0])
                dep_end = int(dep["DEP_SPAN"].split(",")[1])

                tag = pos_tags.getAnnotBySpan(dep_start, dep_end)
                if tag is not None:
                    if tag["TAG"] in ("NNP", "NNPS"):
                        heads2qp[head].prp_mod += 1
                    elif tag["TAG"] in ("NN", "NNS"):
                        heads2qp[head].nom_mod += 1

        if dep["RELATION"] == "num":
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].num_mod += 1

        if dep["RELATION"] == "poss":
            #the possessed
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].poss_mod += 1
            elif dep_key == dep["DEP_SPAN"]:
                #the possessor
                heads2qp[head].is_poss += 1

        #NOTE prep_ can appear more than once for a single noun, which throws
        #off percentages
        if dep["RELATION"] in ("prep_of"):
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].prep_mod += 1

        if dep["RELATION"] in ("rcmod"):
            if dep_key == dep["GOV_SPAN"]:
                heads2qp[head].rc_mod += 1

    #NOTE: modification levels should be low
    if (text == "the " + head) or \
            (text == "that " + head) or \
            (text == "this " + head) or \
            (text == "those " + head) or \
            (text == "these " + head):
        heads2qp[head].bare_definite += 1

    if (text.startswith("the ")):
        heads2qp[head].definite += 1
    if (text.startswith("a ")):
        heads2qp[head].indefinite += 1

def processACE(f, np, heads2qp):
    ace_annots = reconcile.parseGoldAnnots(f)
    stanford_deps = reconcile.getStanfordDep(f)
    gold_chains = reconcile.getGoldChains(f)
    ace_np = ace_annots.getAnnotBySpan(np.getStart(), np.getEnd())

    if ace_np["is_nominal"]:
        head = utils.textClean(ace_np["HEAD"].strip().lower())
        text = utils.textClean(np.getText())

        #bookkeeping
        if head not in list(heads2qp.keys()):
            heads2qp[head] = QuasiPronoun(head)
        else:
            heads2qp[head].updateDocs(f)
            heads2qp[head].updateCount()

        if ace_np["GOLD_SINGLETON"]:
            heads2qp[head].singelton += 1
        else:
            #does it start the chain?
            for gc in list(gold_chains.keys()):
                if gold_chains[gc][0] == np:
                    heads2qp[head].starts_chain += 1
                    break

        process(f, np, head, text, heads2qp, stanford_deps)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <file-list>" % (sys.argv[0]))
        sys.exit(1)

    #PREDICTIONS = "features.goldnps/predictions.StanfordSieve.all_commons"
    #PREDICTIONS = "features.goldnps/predictions.StanfordSieve.all_commons_no_pre_clusters"
    PREDICTIONS = "features.goldnps/predictions.StanfordSieve.bare_definites"

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x for x in fileList.readlines() if not x.startswith("#")])

    wordlist = []
    with open(sys.argv[2], 'r') as wordList:
        wordlist.extend([x.strip() for x in wordList.readlines()])

    i=0
    prog = ProgressBar(len(files))
    correct_qps = {}
    incorrect_qps = {}
    for f in files:
        if f.startswith("#"):
            continue
        f=f.strip()
        prog.update_time(i)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        i += 1

        nps = reconcile.getNPs(f)
        gold_chains = reconcile.getGoldChains(f)
        try:
            all_pairs = reconcile.getFauxPairs(f, PREDICTIONS)
        except:
            continue

        response_pairs = []
        for pair in all_pairs:
            if pair[0] is None or pair[1] is None:
                continue
            response_pairs.append(pair)

        labeled_annots = reconcile.labelCorrectPairs(gold_chains, response_pairs)
        for pair in labeled_annots:
            if ACE:
                if pair[2]:
                    processACE(f,pair[1],correct_qps)
                else:
                    processACE(f,pair[1],incorrect_qps)
    sys.stderr.write("\r \r\n")

    print(len(list(correct_qps.keys())))
    print(len(list(incorrect_qps.keys())))

    columns = {}
    with open("/home/ngilbert/public_html/ace.qp.html", 'w') as htmlFile:
        htmlFile.write("<html>\n")
        htmlFile.write("\t<head><title>ACE QP Results</title></head>\n")
        htmlFile.write("\t<body>\n")
        htmlFile.write("<table border=\"1\">\n")
        htmlFile.write("<tr>")
        htmlFile.write("<td>Head</td>")
        htmlFile.write("<td>Count</td>")
        htmlFile.write("<td>isSubj</td>")
        htmlFile.write("<td>isDobj</td>")
        htmlFile.write("<td>isIobj</td>")
        htmlFile.write("<td>isBareDef</td>")
        htmlFile.write("<td>isDef</td>")
        htmlFile.write("<td>isIndef</td>")
        htmlFile.write("<td>isBA</td>")
        htmlFile.write("<td>Appos1</td>")
        htmlFile.write("<td>Appos2</td>")
        htmlFile.write("<td>Agent</td>")
        htmlFile.write("<td>Adj Mod</td>")
        htmlFile.write("<td>Adv Mod</td>")
        htmlFile.write("<td>Proper Mod</td>")
        htmlFile.write("<td>Common Mod</td>")
        htmlFile.write("<td>Num Mod</td>")
        htmlFile.write("<td>Poss Mod</td>")
        htmlFile.write("<td>isPoss</td>")
        htmlFile.write("<td>Prep Mod</td>")
        htmlFile.write("<td>RC Mod</td>")
        htmlFile.write("</tr>")

        for word in wordlist:
            htmlFile.write("<tr>\n")
            correct_word = correct_qps.get(word, None)
            incorrect_word = incorrect_qps.get(word, None)
            htmlFile.write("<td>{0}</td>".format(word))
            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.count,
                0 if incorrect_word is None else incorrect_word.count,
                ))

            if correct_word is not None:
                columns["c_correct"] = columns.get("c_correct",0) + correct_word.count
            if incorrect_word is not None:
                columns["c_incorrect"] = columns.get("c_incorrect",0) + incorrect_word.count

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.subj,
                0 if incorrect_word is None else incorrect_word.subj,
                ))

            if correct_word is not None:
                columns["subj_correct"] = columns.get("subj_correct",0) + correct_word.subj
            if incorrect_word is not None:
                columns["subj_incorrect"] = columns.get("subj_incorrect",0) + incorrect_word.subj

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.dobj,
                0 if incorrect_word is None else incorrect_word.dobj,
                ))

            if correct_word is not None:
                columns["dobj_correct"] = columns.get("dobj_correct",0) + correct_word.dobj
            if incorrect_word is not None:
                columns["dobj_incorrect"] = columns.get("dobj_incorrect",0) + incorrect_word.dobj

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.iobj,
                0 if incorrect_word is None else incorrect_word.iobj,
                ))
            if correct_word is not None:
                columns["iobj_correct"] = columns.get("iobj_correct",0) + correct_word.iobj
            if incorrect_word is not None:
                columns["iobj_incorrect"] = columns.get("iobj_incorrect",0) + incorrect_word.iobj

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.bare_definite,
                0 if incorrect_word is None else incorrect_word.bare_definite,
                ))
            if correct_word is not None:
                columns["bd_correct"] = columns.get("bd_correct",0) + correct_word.bare_definite
            if incorrect_word is not None:
                columns["bd_incorrect"] = columns.get("bd_incorrect",0) + incorrect_word.bare_definite

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.definite,
                0 if incorrect_word is None else incorrect_word.definite,
                ))
            if correct_word is not None:
                columns["def_correct"] = columns.get("def_correct",0) + correct_word.definite
            if incorrect_word is not None:
                columns["def_incorrect"] = columns.get("def_incorrect",0) + incorrect_word.definite

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.indefinite,
                0 if incorrect_word is None else incorrect_word.indefinite,
                ))
            if correct_word is not None:
                columns["indef_correct"] = columns.get("indef_correct",0) + correct_word.indefinite
            if incorrect_word is not None:
                columns["indef_incorrect"] = columns.get("indef_incorrect",0) + incorrect_word.indefinite

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.starts_chain,
                0 if incorrect_word is None else incorrect_word.starts_chain,
                ))
            if correct_word is not None:
                columns["ba_correct"] = columns.get("ba_correct",0) + correct_word.starts_chain
            if incorrect_word is not None:
                columns["ba_incorrect"] = columns.get("ba_incorrect",0) + incorrect_word.starts_chain

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.appos_gov,
                0 if incorrect_word is None else incorrect_word.appos_gov,
                ))
            if correct_word is not None:
                columns["agov_correct"] = columns.get("agov_correct",0) + correct_word.appos_gov
            if incorrect_word is not None:
                columns["agov_incorrect"] = columns.get("agov_incorrect",0) + incorrect_word.appos_gov

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.appos_dep,
                0 if incorrect_word is None else incorrect_word.appos_dep,
                ))
            if correct_word is not None:
                columns["adep_correct"] = columns.get("adep_correct",0) + correct_word.appos_dep
            if incorrect_word is not None:
                columns["adep_incorrect"] = columns.get("adep_incorrect",0) + incorrect_word.appos_dep

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.agent,
                0 if incorrect_word is None else incorrect_word.agent,
                ))
            if correct_word is not None:
                columns["agent_correct"] = columns.get("agent_correct", 0) + correct_word.agent
            if incorrect_word is not None:
                columns["agent_incorrect"] = columns.get("agent_incorrect", 0) + incorrect_word.agent

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.adj_mod,
                0 if incorrect_word is None else incorrect_word.adj_mod,
                ))
            if correct_word is not None:
                columns["adj_correct"] = columns.get("adj_correct",0) + correct_word.adj_mod
            if incorrect_word is not None:
                columns["adj_incorrect"] = columns.get("adj_incorrect",0) + incorrect_word.adj_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.adv_mod,
                0 if incorrect_word is None else incorrect_word.adv_mod,
                ))
            if correct_word is not None:
                columns["adv_correct"] = columns.get("adv_correct",0) + correct_word.adv_mod
            if incorrect_word is not None:
                columns["adv_incorrect"] = columns.get("adv_incorrect",0) + incorrect_word.adv_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.prp_mod,
                0 if incorrect_word is None else incorrect_word.prp_mod,
                ))
            if correct_word is not None:
                columns["prp_correct"] = columns.get("prp_correct",0) + correct_word.nn_mod
            if incorrect_word is not None:
                columns["prp_incorrect"] = columns.get("prp_incorrect",0) + incorrect_word.nn_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.nom_mod,
                0 if incorrect_word is None else incorrect_word.nom_mod,
                ))
            if correct_word is not None:
                columns["nom_correct"] = columns.get("nom_correct",0) + correct_word.nn_mod
            if incorrect_word is not None:
                columns["nom_incorrect"] = columns.get("nom_incorrect",0) + incorrect_word.nn_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.num_mod,
                0 if incorrect_word is None else incorrect_word.num_mod,
                ))
            if correct_word is not None:
                columns["num_correct"] = columns.get("num_correct",0) + correct_word.num_mod
            if incorrect_word is not None:
                columns["num_incorrect"] = columns.get("num_incorrect",0) + incorrect_word.num_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.poss_mod,
                0 if incorrect_word is None else incorrect_word.poss_mod,
                ))
            if correct_word is not None:
                columns["poss_correct"] = columns.get("poss_correct",0) + correct_word.poss_mod
            if incorrect_word is not None:
                columns["poss_incorrect"] = columns.get("poss_incorrect",0) + incorrect_word.poss_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.is_poss,
                0 if incorrect_word is None else incorrect_word.is_poss,
                ))
            if correct_word is not None:
                columns["iposs_correct"] = columns.get("iposs_correct",0) + correct_word.is_poss
            if incorrect_word is not None:
                columns["iposs_incorrect"] = columns.get("iposs_incorrect",0) + incorrect_word.is_poss

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.prep_mod,
                0 if incorrect_word is None else incorrect_word.prep_mod,
                ))
            if correct_word is not None:
                columns["prep_correct"] = columns.get("prep_correct",0) + correct_word.prep_mod
            if incorrect_word is not None:
                columns["prep_incorrect"] = columns.get("prep_incorrect",0) + incorrect_word.prep_mod

            htmlFile.write("<td><font color=\"green\">{0}</font>/<font color=\"red\">{1}</font></td>".format(
                0 if correct_word is None else correct_word.rc_mod,
                0 if incorrect_word is None else incorrect_word.rc_mod,
                ))
            if correct_word is not None:
                columns["rc_correct"] = columns.get("rc_correct",0) + correct_word.rc_mod
            if incorrect_word is not None:
                columns["rc_incorrect"] = columns.get("rc_incorrect",0) + incorrect_word.rc_mod

            htmlFile.write("</tr>\n")

        htmlFile.write("<tr>\n")
        htmlFile.write("<td> &nbsp; </td>")
        num = float(columns["c_correct"])
        denom = columns["c_correct"] + columns["c_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["subj_correct"])
        denom = columns["subj_correct"] + columns["subj_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["dobj_correct"])
        denom = columns["dobj_correct"] + columns["dobj_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["iobj_correct"])
        denom = columns["iobj_correct"] + columns["iobj_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["bd_correct"])
        denom = columns["bd_correct"] + columns["bd_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["def_correct"])
        denom = columns["def_correct"] + columns["def_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["indef_correct"])
        denom = columns["indef_correct"] + columns["indef_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["ba_correct"])
        denom = columns["ba_correct"] + columns["ba_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["agov_correct"])
        denom = columns["agov_correct"] + columns["agov_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["adep_correct"])
        denom = columns["adep_correct"] + columns["adep_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["agent_correct"])
        denom = columns["agent_correct"] + columns["agent_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["adj_correct"])
        denom = columns["adj_correct"] + columns["adj_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["adv_correct"])
        denom = columns["adv_correct"] + columns["adv_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["prp_correct"])
        denom = columns["prp_correct"] + columns["prp_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["nom_correct"])
        denom = columns["nom_correct"] + columns["nom_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["num_correct"])
        denom = columns["num_correct"] + columns["num_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["poss_correct"])
        denom = columns["poss_correct"] + columns["poss_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["iposs_correct"])
        denom = columns["iposs_correct"] + columns["iposs_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["prep_correct"])
        denom = columns["prep_correct"] + columns["prep_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        num = float(columns["rc_correct"])
        denom = columns["rc_correct"] + columns["rc_incorrect"]
        try:
            htmlFile.write("<td>{0:0.2f}</td>".format(num/denom))
        except:
            htmlFile.write("<td>0.0</td>")

        htmlFile.write("</tr>\n")
        htmlFile.write("</table>\n")
        htmlFile.write("</body></html>\n")
