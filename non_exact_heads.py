#!/usr/bin/python
# File Name : non_exact_heads.py
# Purpose :
# Creation Date : 05-11-2011
# Last Modified : Thu 19 May 2011 05:09:18 PM MDT
# Created By : Nathan Gilbert
#
import sys

from nltk.corpus import wordnet as wn

from . import string_match
from . import data

def getPairs(nps):
    """ list(Annotations) -> list(tuples(Annotations), "non_exact_heads") """

    pairs=[]
    for i in range(0, len(nps)-1):
        np1=nps[i]

        #get rid of pronouns
        if np1.getATTR("pronoun") != "NONE":
            continue

        head1 = np1.getText().split()[-1]
        pre1 = ' '.join(np1.getText().split()[:-1])

        head1=string_match.remove_determiners(head1)
        pre1=string_match.remove_determiners(pre1)
        
        pre_head1 = string_match.getHead(pre1)
        mod1_synsets=wn.synsets(pre_head1)
        if mod1_synsets == []:
            continue
        else:
            mod1_synsets = mod1_synsets[0].lemma_names

        #get rid of pronouns and weird head-modifier string matches
        if (pre1.strip()=="") or (string_match.exact_match(pre1,head1)):
            continue

        if (pre1.lower().strip() in data.ALL_PRONOUNS):
            continue

        for j in range(i+1,len(nps)):
            np2=nps[j]

            #get rid of pronouns
            if np2.getATTR("pronoun") != "NONE":
                continue

            head2 = np2.getText().split()[-1]
            pre2 = ' '.join(np2.getText().split()[:-1])

            head2=string_match.remove_determiners(head2)
            pre2=string_match.remove_determiners(pre2)

            pre_head2 = string_match.getHead(pre2)
            mod2_synsets=wn.synsets(pre_head2)
            if mod2_synsets == []:
                continue
            else:
                mod2_synsets = mod2_synsets[0].lemma_names

            if (pre2.lower().strip() in data.ALL_PRONOUNS):
                continue

            if (pre2.strip()=="") or (string_match.exact_match(pre2,head1)):
                continue

            #this version looks for direct string matches between the two sets
            #pre-modifiers.
            #if string_match.exact_match(pre1,pre2,False) \
            #and not string_match.exact_match(head1,head2,False):
            #    if np1 < np2:
            #        pairs.append((np1,np2,"non-exact-head"))
            #    else:
            #        pairs.append((np1,np2,"non-exact-head"))

            #this versions looks for pre-modifiers that occur in the same
            #synsets as each other. (or atleast their heads do...)
            if not string_match.exact_match(pre1, pre2, False) \
            and not string_match.exact_match(head1, head2, False) \
            and not string_match.guantlet(pre_head1, pre_head2) \
            and mod1_synsets[0] == mod2_synsets[0]:
               if np1 < np2:
                   pairs.append((np1,np2,"non-exact-head"))
               else:
                   pairs.append((np1,np2,"non-exact-head"))
    return pairs

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(("Usage: %s <first-argument>" % (sys.argv[0])))
        sys.exit(1)


