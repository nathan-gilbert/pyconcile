#!/usr/bin/python
# File Name : head_accuracy.py
# Purpose : return the pairwise accuracy of a given set of heads for a given
# coref model.
# Creation Date : 05-24-2013
# Last Modified : Tue 04 Jun 2013 12:03:27 PM MDT
# Created By : Nathan Gilbert
#
import sys

from pyconcile import reconcile
from pyconcile import score
from pyconcile import utils
import specificity_utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filelist> <vp-list>" % (sys.argv[0]))
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend([x.strip() for x in [x for x in fileList.readlines() if not
            x.startswith("#")]])

    heads = []
    with open(sys.argv[2], 'r') as headFile:
        for line in headFile:
            if line.startswith("head") : continue #skip the first line
            line = line.strip()
            if line == "": continue #skip blank lines
            tokens = line.split()
            heads.append(tokens[0])

    #I want to track the accuracy of individual heads.
    head2correct = {}    #heads that have a correct antecedent.
    head2wrong   = {}    #heads that have an incorrect antecedent. appears in a
                         #chain with nothing else it is coreferent with
    head2none    = {}    #heads that were not given an antecedent. --focus on
                         #this one first
    head2counts  = {}

    outputfile = "/features.goldnps/predictions.StanfordSieve.stanfordsieve/SingleLink"
    for f in files:
        #gather all the chains that were generated by the system.
        gold_chains = reconcile.getGoldChains(f)
        response_chains = reconcile.getResponseChains(f, outputfile)
        nps = reconcile.getNPs(f)

        for np in nps:
            head = specificity_utils.getHead(utils.textClean(np.getText())).lower()
            if head in heads:
                #this is the number of times that a NP appeared in a doc
                head2counts[head] = head2counts.get(head, 0) + 1
            #print "{0} : {1}".format(np.pprint(), head)

        #for chain in response_chains:
        #    if len(response_chains[chain]) > 1:
        #        for mention in response_chains[chain]:
        #            print mention.pprint()
        #        print

        #find all the gold vps that were not assigned any cluster.
        for chain in list(response_chains.keys()):
            if len(response_chains[chain]) == 1:
                mention = response_chains[chain][0]
                head = specificity_utils.getHead(utils.textClean(mention.getText())).lower()
                if head in heads:
                    #this is the # number of times the classifier did not even
                    #attempt to place this NP in a chain.
                    head2none[head] = head2none.get(head, 0) + 1
            else:
                #count the number of times a vp is in a chain only with things it
                #does not corefer with.

                #find the vps
                vps = []
                for mention in response_chains[chain]:
                    head = specificity_utils.getHead(utils.textClean(mention.getText())).lower()
                    if head in heads:
                        vps.append(mention)

                if len(vps) > 0:
                    for vp in vps:
                        found_antecedent = False
                        for mention in response_chains[chain]:
                            if vp == mention:
                                continue

                            head = specificity_utils.getHead(utils.textClean(mention.getText())).lower()
                            if score.correctpair(gold_chains, mention, vp):
                                found_antecedent = True

                        if not found_antecedent:
                            head = specificity_utils.getHead(utils.textClean(vp.getText())).lower()
                            head2wrong[head] = head2wrong.get(head, 0) + 1

    total_not_found = 0
    total_wrong = 0
    for head in list(head2none.keys()):
        print("{0:13} : {1:2} / {2:2} = {3:0.2f} | {4:2} / {5:2} = {6:0.2f} ".format(head, head2none[head],
                head2counts[head], float(head2none[head]) / head2counts[head],
                head2wrong.get(head, 0), head2counts[head],
                float(head2wrong.get(head,0)) / head2counts[head]))

        total_not_found += head2none[head]
        total_wrong += head2wrong.get(head, 0)
    print("{0} total vps missing antecedents.".format(total_not_found))
    print("{0} totally wrong vps".format(total_wrong))
