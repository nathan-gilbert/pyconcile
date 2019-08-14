#!/usr/bin/python
# File Name : lkb-lib.py
# Purpose : Libraries useful for lkb.
# Creation Date : 01-30-2013
# Last Modified : Mon 08 Apr 2013 09:21:10 AM MDT
# Created By : Nathan Gilbert
#
import sys
import operator

from entry import Entry

def read_in_lkb(lkb_file_name):
    """
    read in a lkb
    """
    lkb = {}
    with open(lkb_file_name, 'r') as lkb_file:
        ces = False
        nes = False
        doc_count = False
        self_tags = False
        current_entry = Entry()
        for line in lkb_file:
            line=line.strip()
            if line.startswith("#"):
                continue
            if line.startswith("TEXT:"):
                text = line.replace("TEXT: ", "").strip()
                current_entry.setText(text)
            elif line.startswith("ID: "):
                #don't really need to do anything with this
                entry_id = line.replace("ID: ","").strip()
            elif line.startswith("Count: "):
                count = int(line.replace("Count: ","").strip())
                current_entry.setCount(count)
            elif line.startswith("=Doc Count Begin="):
                doc_count = True
            elif line.find("$!$") > -1 and doc_count:
                tokens=line.split("$!$")
                current_entry.setDocCount(tokens[0].strip(), int(tokens[1].strip()))
            elif line.startswith("=Doc Count End="):
                doc_count = False
            elif line.startswith("=CEs Begin="):
                ces = True
            elif line.find("$!$") > -1 and ces:
                tokens = line.split("$!$")
                for i in range(int(tokens[2].strip())):
                    current_entry.addCoref(tokens[0].strip(),
                            tokens[1].strip())
            elif line.startswith("=CEs End="):
                ces = False
            elif line.startswith("=Self Tags Begin"):
                self_tags = True
            elif line.find("$!$") > -1 and self_tags:
                tokens = line.split("$!$")
                for i in range(int(tokens[2].strip())):
                    current_entry.setSemanticTag(tokens[0].strip(),
                            tokens[1].strip())
            elif line.startswith("=Self Tags End"):
                self_tags = False
            elif line.startswith("=Semantic Begin="):
                nes = True
            elif line.find("$!$") > -1 and nes:
                tokens = line.split("$!$")
                for i in range(int(tokens[3].strip())):
                    current_entry.addSemantic(tokens[0].strip(),
                            tokens[1].strip(), tokens[2].strip())
            elif line.startswith("=Semantic End="):
                nes = False
            elif line == "$!$":
                #add the entry to the database
                lkb[text] = current_entry
                current_entry = Entry()
            else:
                sys.stderr.write("Error: line not found ->" + line)
    return lkb

def sort_lkb_by_count(lkb):
    #TODO
    sorted_lkb = sorted(iter(lkb.items()), key=operator.itemgetter(1).getCount(), reverse=True)
    return sorted_lkb

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <first-argument>" % (sys.argv[0]))
        sys.exit(1)

    print("Does nothing!")

