#!/usr/bin/python
# File Name : semantic_classes.py
# Purpose : 
# Creation Date : 01-31-2013
# Last Modified : Thu 11 Apr 2013 09:20:01 AM MDT
# Created By : Nathan Gilbert
#
import sys
from operator import itemgetter

from pyconcile import reconcile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <first-argument>" % (sys.argv[0])
        sys.exit(1)

    fList = open(sys.argv[1], 'r')
    classes = {}
    total_nps = 0
    for f in fList:
        f=f.strip()
        if f.startswith("#"):
            continue
        gold_nps = reconcile.getNPs(f)
        reconcile.addSundanceProps(f, gold_nps)
        for np in gold_nps:
            total_nps += 1
            #for sundance
            nes = np.getATTR("SUN_SEMANTIC")
            if nes is not None:
                for ne in nes:
                    #classes[ne] = classes.get(ne, 0) + 1
                    #print "{0:50} => {1}".format(np.getText().replace("\n", " "), ne)
                    print "{0}".format(ne)
            #for wordnet
            #synsets = np.getATTR("SYNSETS")
            #if len(synsets) > 0:
               #for ne in synsets[0]:
                   #classes[ne] = classes.get(ne, 0) + 1
            #for stanford
            #semantic = np.getATTR("SEMANTIC")
            #if semantic != "UNKNOWN":
               #classes[semantic] = classes.get(semantic, 0) + 1
    #sorted_classes = sorted(classes.iteritems(),
    #        key=itemgetter(1),reverse=True)
    #total_classes = 0
    #for ne in classes.keys():
    #    total_classes += classes[ne]
    #for pair in sorted_classes:
    #    print "{0:30} : {1:3} : {2:.2%} : {3:.2%}".format(pair[0], pair[1],
    #            float(pair[1])/total_classes, float(pair[1])/total_nps)
