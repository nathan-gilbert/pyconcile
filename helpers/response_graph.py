#!/usr/bin/python
# File Name : response_graph.py
# Purpose : Generates a dot graph of Reconcile's responses
# Creation Date : 04-03-2012
# Last Modified : Thu 06 Sep 2012 01:41:23 PM MDT
# Created By : Nathan Gilbert
#
import sys
import pydot

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <response-file>" % (sys.argv[0]))
        sys.exit(1)

    dataDir = sys.argv[1][:sys.argv[1].find("/")]
    responseFile = sys.argv[1][sys.argv[1].find("/"):]
    clusterer="SingleLink"
    sentences = reconcile.getSentences(dataDir)
    gold_chains = reconcile.getGoldChains(dataDir)

    #get reconcile's edges
    response_chains = reconcile.getResponseChains(dataDir,
            responseFile+"/"+clusterer)

    response_pairs = reconcile.getResponsePairs(dataDir, responseFile, 0.5)
    response_pairs = reconcile.labelCorrectPairs(gold_chains, response_pairs)

    #pydot graph
    graph = pydot.Dot("reconcile_clusters", graph_type='digraph')

    #add in all the NP
    #NOTE: as long as we are working with gold mentions, the response and gold
    #will match. otherwise, will need to switch over to gold nps to see proper
    #'misses'
    for key in list(response_chains.keys()):
        chain = response_chains[key]
        #prev_mention = None
        #prev_txt = ""
        for mention in chain:
            #add a node
            txt = "%s (%d,%d)" % (mention.getText().replace("\n", " ").replace("\"",""),
                    mention.getStart(), mention.getEnd())
            graph.add_node(pydot.Node(txt))

            #if prev_mention is not None:
            #    graph.add_edge(pydot.Edge(txt,prev_txt))
            #prev_mention = mention
            #prev_txt = txt

    i = 0
    for s in sentences:
        subg = pydot.Subgraph('', rank='same')
        for key in list(response_chains.keys()):
            chain = response_chains[key]
            for mention in chain:
                if s.contains(mention):
                    txt = "%s (%d,%d)" % (mention.getText().replace("\n", " ").replace("\"",""),
                            mention.getStart(), mention.getEnd())
                    txt = txt.replace("\"","")
                    txt = txt.replace("\n"," ")
                    subg.add_node(pydot.Node(txt))
        i += 1
        graph.add_subgraph(subg)

    #the pairs
    for pair in response_pairs:
        antecedent = pair[0]
        anaphor = pair[1]
        truth = pair[2]

        ant_txt = "%s (%d,%d)" % (antecedent.getText().replace("\n", " ").replace("\"",""),
                    antecedent.getStart(), antecedent.getEnd())

        ana_txt = "%s (%d,%d)" % (anaphor.getText().replace("\n", " ").replace("\"",""),
                    anaphor.getStart(), anaphor.getEnd())

        #print "%s <- %s" % (ant_txt, ana_txt)
        if truth:
            graph.add_edge(pydot.Edge(ant_txt, ana_txt, dir="back"))
        else:
            graph.add_edge(pydot.Edge(ant_txt, ana_txt, color="red", dir="back"))

    #write out the coreference graph
    #graph.write_dot('graph.dot')
    graph.write_png('./graph.png')
