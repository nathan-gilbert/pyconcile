#!/usr/bin/python
'''
Created on Aug 1, 2011
Last Modified : Mon 15 Aug 2011 01:29:31 PM MDT
@author: ngilbert
'''

import sys
from optparse import OptionParser

from pyconcile import reconcile
from pyconcile import annotation_set

class ModList:
    def __init__(self, name):
        self.name = name
        self.container = []

    def add(self, mod):
        for m in self.container:
            if m.getText() == mod.getText():
                m.update(mod)
                break
        else:
            self.container.append(mod)

    def __iter__(self):
        return self.forward()

    def forward(self):
        for a in self.container:
            yield a

class Modifier:
    def __init__(self, t, attr, modded):
        self.text = t.lower().strip()       #the text
        self.attr = attr                    #any useful attributes for this modifier
        self.count = 1                      #count how many times this text is used as a modifier
        self.modifiedText = [modded]        #the text that got modified

    def updateCount(self):
        self.count += 1

    def getText(self):
        return self.text

    def getCount(self):
        return self.count

    def addMods(self, m):
        self.modifiedText.append(m)

    def getMods(self):
        return self.modifiedText

    def update(self, other):
        self.modifiedText.extend(other.getMods())
        self.updateCount()

    def __str__(self):
        modded = ', '.join(self.modifiedText)
        s = "%d : %s (Mods: %s)" % (self.count, self.text, modded)
        return s

if __name__ == '__main__':
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--filelist", dest="filelist",
            help="The filelist to process", type="string", action="store",
            default="tmp.list")
    parser.add_option("-v", help="Verbose. Be it.", action="store_true",
            dest="verbose", default=False)
    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    mods_list = ModList("modifiers")

    filelist = open(options.filelist, 'r')
    for dir in filelist:
        dir = dir.strip()
        nps = reconcile.getNPs_annots(dir)

        for np in nps:
            if not np.getATTR("is_common"):
                continue

            if np.getATTR("MODIFIER").strip() != "":
                mod = Modifier(np.getATTR("MODIFIER"), {}, np.getText())
                mods_list.add(mod)

    for m in mods_list:
        print m
