#!/usr/bin/python
# File Name : gold_graph.py
# Purpose : Generates a dot graph 
# Creation Date : 04-18-2012
# Last Modified : Fri 27 Apr 2012 11:34:57 AM MDT
# Created By : Nathan Gilbert
#
import sys
import pydot

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <datadir>" % (sys.argv[0]))
        sys.exit(1)

    dataDir = sys.argv[1]
    gold_chains = reconcile.getGoldChains(dataDir)
    gold_sentences = reconcile.getSentences(dataDir)
    gold_pairs = []

    #pydot graph
    graph = pydot.Dot("gold_clusters", graph_type='digraph')

    #add in all the NP
    for key in list(gold_chains.keys()):
        chain = gold_chains[key]
        prev = None
        for mention in chain:
            #add a node
            txt = "%s (%d,%d)" % (mention.getText(),
                    mention.getStart(), mention.getEnd())
            txt = txt.replace("\"","")
            txt = txt.replace("\n"," ")
            graph.add_node(pydot.Node(txt))

            if prev is not None:
                gold_pairs.append((prev, mention))
            prev = mention

    i = 0
    for s in gold_sentences:
        subg = pydot.Subgraph('', rank='same')
        for key in list(gold_chains.keys()):
            chain = gold_chains[key]
            for mention in chain:
                if s.contains(mention):
                    txt = "%s (%d,%d)" % (mention.getText(),
                            mention.getStart(), mention.getEnd())
                    txt = txt.replace("\"","")
                    txt = txt.replace("\n"," ")
                    subg.add_node(pydot.Node(txt))
        i += 1
        graph.add_subgraph(subg)

    #the pairs
    for pair in gold_pairs:
        antecedent = pair[0]
        anaphor = pair[1]

        ant_txt = "%s (%d,%d)" % (antecedent.getText(),
                    antecedent.getStart(), antecedent.getEnd())
        ant_txt = ant_txt.replace("\"","")
        ant_txt = ant_txt.replace("\n"," ")

        ana_txt = "%s (%d,%d)" % (anaphor.getText(),
                    anaphor.getStart(), anaphor.getEnd())
        ana_txt = ana_txt.replace("\"","")
        ana_txt = ana_txt.replace("\n"," ")

        graph.add_edge(pydot.Edge(ant_txt, ana_txt, dir="back"))

    #write out the coreference graph
    graph.write_png('gold_graph.png')
    #graph.write_dot('graph.dot')
