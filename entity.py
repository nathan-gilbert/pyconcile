'''
Purpose : Super Annotation to collect stats over many annotations across docs
Created on Jul 13, 2011
Last Modified : 
@author: ngilbert
'''

from annotation import Annotation

class Entity(object):
    '''
    classdocs
    '''

    def __init__(self, n):
        '''
        Constructor
        '''
        self.name = n
        self.count = 0
        self.texts = []
        self.mins = []
        self.heads = []
        self.semantics = {}
        self.postags = {}
        self.types = {}
        self.trigrams = {}
        self.subject_verbs = {}
        self.object_verbs = {}
        self.modifiers = {}
    
    def __str__(self):
        s = ""
        s += "name: %s (%d)" % (self.name, self.count)
        
    def addAnnot(self, a):
        self.addText(a.getATTR("TEXT"))
        self.addMins(a.getATTR("MIN"))
        self.addSemantics(a.getATTR("SEMANTIC"))
        self.addSemantics(a.getATTR("SUN_SEMANTICS"))
        self.addType(a.getATTR("TYPE"))
        self.addModifier(a.getATTR("MODIFIER"))
        self.count += 1
        
    def addText(self, t):
        self.texts.append(t)
       
    def addMins(self, m):
        self.mins.append(m)
        
    def addHead(self, h):
        self.heads.append(h) 
        
    def addModifier(self, m):
        self.modifiers[m] = self.modifiers.get(m, 0) + 1
        
    def addSemantics(self, sem):
        self.semantics[sem] = self.semantics.get(sem, 0) + 1
    
    def addPOStags(self, tag):
        self.postags[tag] = self.postags.get(tag, 0) + 1

    def addType(self, t):
        self.types[t] = self.types.get(t, 0) + 1

    def addTrigram(self, tri):
        tri = tri.lower()
        self.trigrams[tri] = self.trigrams.get(tri, 0) + 1

    def addSubj(self, v):
        v = v.lower()
        self.subject_verbs[v] = self.subject_verbs.get(v, 0) + 1

    def addObj(self, v):
        v = v.lower()
        self.object_verbs[v] = self.object_verbs.get(v, 0) + 1
