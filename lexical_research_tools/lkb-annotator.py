#!/usr/bin/python
# File Name : lkb-annotator.py
# Purpose : Qualitatively annotated elements in the LKB
# Creation Date : 03-08-2013
# Last Modified : Sat 04 May 2013 12:37:08 PM MDT
# Created By : Nathan Gilbert
#
import sys
import os
import subprocess

import lkb_lib
from entry import Entry
from pyconcile import data

HEAD_CACHE = {}

def readInCache():
    tags = {}
    try:
        with open("annotation.cache", 'r') as inFile:
            for line in inFile:
                line = line.strip()
                tokens = line.split("$!$")
                tags[tokens[0].strip()] = tokens[1].strip()
        return tags
    except:
        return None

def writeOutCache(tags):
    with open("annotation.cache", 'w') as outFile:
        for key in list(tags.keys()):
            outFile.write("{0}$!${1}\n".format(key,tags[key]))

def getHead(text):
    global HEAD_CACHE

    if text not in list(HEAD_CACHE.keys()):
        p1 = subprocess.Popen(["/usr/bin/java", "ReconcileStringFormat",
            "\"{0}\"".format(text)], stdout=subprocess.PIPE)
        head = p1.stdout.read().replace("\"","").strip()
        HEAD_CACHE[text] = head
        return head
    else:
        return HEAD_CACHE[text]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <lkb-file>" % (sys.argv[0]))
        sys.exit(1)

    previous_tags = readInCache()
    tagged_resolutions = {} if (previous_tags is None) else previous_tags

    #read in lkb
    lkb = lkb_lib.read_in_lkb(sys.argv[1])

    #cycle over the pairs and annotated them.
    annotated = 0
    total_annotations = 0

    #Startup will take longer as all the heads will now be cached.
    print("Finding total annotations...", end=' ')
    for key in list(lkb.keys()):
        for antecedent in list(lkb[key].getAntecedentCounts().keys()):
            antecedent = getHead(antecedent.strip())
            if key == antecedent:
                continue
            total_annotations += 1
    print("Finished.")

    for key in list(lkb.keys()):
        for antecedent in list(lkb[key].getAntecedentCounts().keys()):
            key = getHead(key.strip())
            antecedent = getHead(antecedent.strip())
            if key == antecedent:
                continue

            pair = "{0}:{1}".format(key, antecedent)
            pair2 = "{0}:{1}".format(antecedent, key)
            annotated += 1
            if (pair in list(tagged_resolutions.keys())) or (pair2 in list(tagged_resolutions.keys())):
                continue
            elif key in data.ALL_PRONOUNS or antecedent in data.ALL_PRONOUNS:
                category = "PRO"
                tagged_resolutions[pair] = category
            else:
                os.system("clear")
                print("Remaining annotations: {0}/{1}".format(annotated,total_annotations))
                print("{0} <= {1}".format(key, antecedent))
                while True:
                    answer = input("Which category? [j=identity, a=synonym, k=hyper, f=pronoun, d=denomination, m=meronymy, o=misc:h ")
                    if answer == "j":
                        category = "IDENT"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "a":
                        category = "SYN"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "k":
                        category = "HYPER"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "f":
                        category = "PRO"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "d":
                        category = "DENOM"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "m":
                        category = "MERON"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "o":
                        category = "MISC"
                        tagged_resolutions[pair] = category
                        break
                    elif answer == "save":
                        writeOutCache(tagged_resolutions)
                        continue
                    elif answer == "quit":
                        writeOutCache(tagged_resolutions)
                        sys.exit(0)
                    else:
                        continue
    writeOutCache(tagged_resolutions)
