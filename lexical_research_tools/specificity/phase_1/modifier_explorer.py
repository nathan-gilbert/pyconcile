#!/usr/bin/python
# File Name : modifier_explorer.py
# Purpose : Catalog characteristics of common noun modifiers.
# Creation Date : 06-04-2013
# Last Modified : Wed 17 Jul 2013 11:40:15 AM MDT
# Created By : Nathan Gilbert
#
import sys
import operator
import collections

from pyconcile import reconcile
from pyconcile import utils
import specificity_utils
from pyconcile.bar import ProgressBar

class Noun:
    def __init__(self, h):
        self.head  = h
        self.count = 1
        self.docs = []
        self.texts = []
        self.bare_definite = 0
        self.indefinite = 0
        self.subject = 0
        self.dobj     = 0
        self.adjective_modifiers = []
        self.common_modifiers    = []
        self.proper_modifiers    = []
        self.other_modifiers     = []
        self.of_attachments      = []
        self.on_attachments      = []
        self.by_attachments      = []
        self.which_attachments   = []
        self.with_attachments    = []
        self.that_attachments    = []
        self.verbed              = []
        self.verbing             = []

def getSortedList(l):
    #adj = [elt for elt,count in collections.Counter(noun.adjective_modifiers).most_common(3)]
    l_items = set(l) # produce the items without duplicates
    l_counts = [ (l.count(x), x) for x in l_items]
    # for every item create a tuple with the number of times the item appears and
    # the item itself
    l_counts.sort(reverse=True)
    # sort the list of items, reversing is so that big items are first
    l_result = [ y for x,y in l_counts ]
    if len(l_result) > 7:
        l_result = l_result[:7]
    return l_result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <file-list>" % (sys.argv[0])
        sys.exit(1)

    files = []
    with open(sys.argv[1], 'r') as fileList:
        files.extend(map(lambda x : x.strip(), filter(lambda x : not
            x.startswith("#"), fileList.readlines())))

    docs_needed = round(float(len(files)) * 0.05)

    head2nouns = {}
    sys.stderr.flush()
    sys.stderr.write("\r")
    prog = ProgressBar(len(files))
    j = 0
    for f in files:
        prog.update_time(j)
        sys.stderr.write("\r%s" % (str(prog)))
        sys.stderr.flush()
        j += 1

        nps = reconcile.getNPs(f)
        pos = reconcile.getPOS(f)
        for np in nps:
            if specificity_utils.isNominal(np):
                np_text = utils.textClean(np.getText()).lower()
                if utils.isConj(np_text): continue

                np_head = specificity_utils.getHead(np_text).lower()
                head_index = specificity_utils.getHeadIndex(np, np_head)
                np_pos = pos.getSubset(np.getStart(), np.getEnd())
                np_words = np_text.split()
                #print "{0:35} -> {1:15}".format(np_text, np_head)

                if np_head not in head2nouns.keys():
                    head2nouns[np_head] = Noun(np_head)
                    head2nouns[np_head].docs.append(f)
                else:
                    head2nouns[np_head].count += 1
                    head2nouns[np_head].docs.append(f)

                if np["GRAMMAR"] == "SUBJECT":
                    head2nouns[np_head].subject += 1
                elif np["GRAMMAR"] == "SUBJECT":
                    head2nouns[np_head].dobj += 1

                #find bare definite nps (could have pp attachments)
                definite = "the {0}".format(np_head.strip())
                indefinite1 = "a {0}".format(np_head.strip())
                indefinite2 = "an {0}".format(np_head.strip())
                if np_text.startswith(definite):
                    head2nouns[np_head].bare_definite += 1
                if np_text.startswith(indefinite1) or np_text.startswith(indefinite2):
                    head2nouns[np_head].indefinite += 1
                elif np_text.startswith("the"):
                    #get parts of speech for the np:
                    if len(np_pos) != len(np_words):
                        #sys.stderr.write("Mismatch tag and word length: {0} => {1}\n".format(np_pos.getList(), np_words))
                        continue

                    for i in range(0, head_index):
                        if np_pos[i]["TAG"] == "DT":
                            continue
                        elif np_pos[i]["TAG"] == "JJ":
                            #print "Adjective: {0}".format(np_words[i])
                            head2nouns[np_head].adjective_modifiers.append(np_words[i])
                        elif np_pos[i]["TAG"].startswith("N"):
                            #print "Noun: {0} {1}".format(np_words[i], np_pos[i]["TAG"])
                            if np_pos[i]["TAG"].startswith("NNP"):
                                head2nouns[np_head].proper_modifiers.append(np_words[i])
                            else:
                                head2nouns[np_head].common_modifiers.append(np_words[i])
                        else:
                            #print "?: {0}".format(np_words[i])
                            head2nouns[np_head].other_modifiers.append(np_words[i])

                #capture post modifiers
                if np_text.find(np_head + " of ") > -1:
                    of_start = np_text.find(np_head + " of ")
                    of_object = np_text[len(np_head) + of_start + 3:]
                    head2nouns[np_head].of_attachments.append(of_object.strip())

                if np_text.find(np_head + " on ") > -1:
                    of_start = np_text.find(np_head + " on ")
                    of_object = np_text[len(np_head) + of_start + 3:]
                    head2nouns[np_head].on_attachments.append(of_object.strip())

                if np_text.find(np_head + " that ") > -1:
                    that_start = np_text.find(np_head + " that ")
                    that_clause = np_text[len(np_head) + that_start+5:]
                    head2nouns[np_head].that_attachments.append(that_clause.strip())

                if np_text.find(np_head + " with ") > -1:
                    that_start = np_text.find(np_head + " with ")
                    that_clause = np_text[len(np_head) + that_start+5:]
                    head2nouns[np_head].with_attachments.append(that_clause.strip())

                if np_text.find(np_head + " by ") > -1:
                    by_start = np_text.find(np_head + " by ")
                    by_object = np_text[len(np_head) + by_start+3:]
                    head2nouns[np_head].by_attachments.append(by_object.strip())

                if np_text.find(np_head + " which ") > -1:
                    which_start = np_text.find(np_head + " which ")
                    which_clause = np_text[len(np_head) + which_start+6:]
                    head2nouns[np_head].which_attachments.append(which_clause.strip())

                if len(np_pos) >= head_index+2 and len(np_words) >= head_index+2:
                    if np_pos[head_index+1]["TAG"] == "VBD":
                        head2nouns[np_head].verbed.append(np_words[head_index+1])

                    if np_pos[head_index+1]["TAG"] == "VBG":
                        head2nouns[np_head].verbing.append(np_words[head_index+1])

    sys.stderr.write("\r \r\n")
    sorted_nouns = sorted(head2nouns.values(), key=operator.attrgetter('count'), reverse=True)
    for noun in sorted_nouns:
        if len(set(noun.docs)) < docs_needed:
            continue

        print "{0:15} {1:>5} {2:>4} {3:>4} {4:>4} {5:>4} {6:>4} {7:>4} {8:>4} {9:>4}".format(
                "head",
                "count",
                "bd",
                "ind",
                "adj",
                "prp",
                "nom",
                "oth",
                "sub",
                "obj"
               )
        print

        bare_definite = float(noun.bare_definite) / noun.count
        indefinite   = float(noun.indefinite) / noun.count
        print "{0:15} {1:5} {2:0.2f} {3:0.2f} {4:0.2f} {5:0.2f} {6:0.2f} {7:0.2f} {8:0.2f} {9:0.2f}".format(
                noun.head,
                noun.count,
                bare_definite,
                indefinite,
                float(len(noun.adjective_modifiers)) / noun.count ,
                float(len(noun.proper_modifiers)) / noun.count,
                float(len(noun.common_modifiers)) / noun.count,
                float(len(noun.other_modifiers)) / noun.count,
                float(noun.subject) / noun.count,
                float(noun.dobj) / noun.count
                )

        adj_list = getSortedList(noun.adjective_modifiers)
        print "{0:>15} {1}".format(
                "adjectives:",
                adj_list
                )
        proper_list = getSortedList(noun.proper_modifiers)
        print "{0:>15} {1}".format(
                "proper:",
                proper_list
                )
        common_list = getSortedList(noun.common_modifiers)
        print "{0:>15} {1}".format(
                "common:",
                common_list
                )
        other_list = getSortedList(noun.other_modifiers)
        print "{0:>15} {1}".format(
                "other:",
                other_list
                )
        of_list = getSortedList(noun.of_attachments)
        print "{0:>15} {1}".format(
                "of attachments:",
                of_list
                )
        on_list = getSortedList(noun.on_attachments)
        print "{0:>15} {1}".format(
                "on attachments:",
                on_list
                )
        by_list = getSortedList(noun.by_attachments)
        print "{0:>15} {1}".format(
                "by attachments:",
                by_list
                )
        that_list = getSortedList(noun.that_attachments)
        print "{0:>15} {1}".format(
                "that clause:",
                that_list
                )
        which_list = getSortedList(noun.which_attachments)
        print "{0:>15} {1}".format(
                "which clause:",
                which_list
                )
        with_list = getSortedList(noun.with_attachments)
        print "{0:>15} {1}".format(
                "with clause:",
                with_list
                )
        verbed_list = getSortedList(noun.verbed)
        print "{0:>15} {1}".format(
                "verbed:",
                verbed_list
                )
        verbing_list = getSortedList(noun.verbing)
        print "{0:>15} {1}".format(
                "verbing:",
                verbing_list
                )
        print

