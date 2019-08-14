#!/usr/bin/python
# File Name : checkReconcileGoldChains.py
# Purpose : To ensure that Reconcile is correctly creating the clusters that
# appear in the annotations
# Creation Date : 09-28-2011
# Last Modified : Fri 30 Sep 2011 01:06:04 PM MDT
# Created By : Nathan Gilbert
#
import sys
import copy
import xml.sax
from xml.sax.handler import ContentHandler
from collections import defaultdict

from pyconcile import reconcile
from pyconcile.annotation_set import AnnotationSet
from pyconcile.annotation import Annotation

#works for ACE04/05
class corefHandler(ContentHandler):
    def __init__(self):
        self.clusters = {}
        self.count = 0
        self.mentionCount = 0
        self.entity = AnnotationSet("entity"+str(self.count))
        self.inEntity = False
        self.inMention = False
        self.inHead = False
        self.attr = {}
        self.text = ""
        self.head = ""
        self.type = ""
        self.subtype = ""
        self.cls = ""
        self.entity_id = ""

    def startElement(self, name, attrs):
        if name == "entity":
            self.inEntity = True
            self.type = attrs.get("TYPE", "None")
            #some PER types do not have a subtype.
            self.subtype = attrs.get("SUBTYPE", "None")
            self.cls = attrs.get("CLASS", "None")
            self.entity_id = attrs["ID"]

        elif name == "entity_mention":
            if self.inEntity:
                self.inMention = True
                for key in list(attrs.keys()):
                    self.attr[key] = attrs[key]
                self.attr["SEMANTIC"] = "%s:%s" % (self.type, self.subtype)
                self.attr["CLASS"] = self.cls
                self.attr["ENTITY_ID"] = self.entity_id

        elif name == "head":
            self.inHead = True

        elif name == "charseq":
            if self.inMention and not self.inHead:
                self.start = int(attrs["START"])
                self.end = int(attrs["END"])

    def endElement(self, name):
        if name == "entity":
            self.inEntity = False
            self.clusters[str(self.count)] = self.entity
            self.count += 1
            self.entity = AnnotationSet("entity"+str(self.count))
            self.text = ""
            self.head = ""

        elif name == "entity_mention":
            self.inMention = False
            self.attr["HEAD"] = self.head.strip()
            self.attr["TEXT"] = self.text.replace("\n", " ").strip()
            self.entity.add(Annotation(self.start, self.end,
                self.mentionCount, copy.deepcopy(self.attr), self.text.strip()))
            self.mentionCount += 1
            self.text = ""
            self.head = ""

        elif name == "head":
            self.inHead = False

    def characters(self, ch):
        if self.inMention:
            if self.inHead:
                self.head += ch
            else:
                self.text += ch

#TODO: MUC6/7
#TODO: ACE03/phase2

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <indir>" % (sys.argv[0]))
        sys.exit(1)


    #read in Reconcile Gold Chains, i.e., what Reconcile thinks are the
    #gold clusters.
    reconcile_gold_chains = reconcile.getGoldChains(sys.argv[1])

    #for chain in reconcile_gold_chains.keys():
    #    print "======="
    #    for mention in reconcile_gold_chains[chain]:
    #        print mention
    #    print "======="

    #read in the key.xml file and parse it 
    xmlFile = open(sys.argv[1]+"/key.xml", 'r')
    parser = xml.sax.make_parser()
    handler = corefHandler()
    parser.setContentHandler(handler)
    parser.parse(xmlFile)
    xmlFile.close()

    ace_gold_chains = handler.clusters

    #for cluster in ace_gold_chains.keys():
    #    print "cluster: %s" % cluster
    #    for mention in ace_gold_chains[cluster]:
    #        print mention

    spans = []
    ace2spans = defaultdict(list)
    for cluster in list(ace_gold_chains.keys()):
        for mention in ace_gold_chains[cluster]:
            key = "%d:%d" % (mention.getStart(), mention.getEnd())
            spans.append(key)
            ace2spans[cluster].append(key)

    rec2spans = defaultdict(list)
    for cluster in list(reconcile_gold_chains.keys()):
        for mention in reconcile_gold_chains[cluster]:
            key = "%d:%d" % (mention.getStart(), mention.getEnd()-1)
            rec2spans[cluster].append(key)

    ace_items = list(ace2spans.items())
    rec_items = list(rec2spans.items())

    for span in spans:
        ace_cluster = "-1"
        rec_cluster = "-1"

        for a in ace_items:
            if span in a[1]:
                ace_cluster = a[0]
                break

        for a in rec_items:
            if span in a[1]:
                rec_cluster = a[0]
                break

        print("%s : %s : %s" % (span, ace_cluster, rec_cluster))



