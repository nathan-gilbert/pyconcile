#!/usr/bin/python
# File Name : annotation_set.py
# Purpose : A container class for annotations.
# Creation Date : 06-24-2011
# Last Modified : Tue 28 Jan 2014 11:57:59 AM MST
# Created By : Nathan Gilbert
# Notes:
#  1. All annotations are stored as ordered list, ordered by span in the
#  document they are drawn from.
#
from annotation import Annotation

class AnnotationSet:
    def __init__(self, n):
        self.container = []
        self.name = n

    def __len__(self):
        return len(self.container)

    def __iter__(self):
        return self.forward()

    def __str__(self):
        s = ""
        for a in self.container:
            s += a.pprint() + "\n"
        return self.name + "\n" + s

    def __getitem__(self, key):
        return self.container[key]

    def pop(self, i=0):
        """Pops the ith item from the set, defaults to the first."""
        return self.container.pop(i)

    def forward(self):
        for a in self.container:
            yield a

    def getName(self):
        return self.name

    def remove(self, i):
        """removes the ith element from the container"""
        del self.container[i]

    def removeAnnot(self, annot):
        remove_index = -1
        j=0
        for a in self.container:
            if a == annot:
                remove_index = j
                break
            j+=1

        if remove_index > -1:
            del self.container[remove_index]

    def removeAnnotByID(self, i):
        remove_index = -1
        for j in range(0, len(self.container)):
            if self.container[j].getID() == i:
                remove_index = j
        if remove_index > -1:
            del self.container[remove_index]

    def add(self, a):
        """Put this annotation in the proper order."""
        if len(self.container) < 1:
            self.container.append(a)
        elif a > self.container[-1]:
            self.container.append(a)
        else:
            for i in range(0, len(self.container)):
                if a < self.container[i]:
                    self.container.insert(i, a)
                    break
            else:
                #catch the case where the next added is truly the last one.
                #*should be captured earlier by the elif
                self.container.append(a)

    def contains(self, annot):
        """Return true if this set has an annotation with the same span as the
        supplied annotation."""
        for a in self.container:
            if a == annot:
                return True
        return False

    def getSubset(self, start, end):
        """Returns a list of annots that fall between the start and end
        provided."""
        subset = AnnotationSet("subset")
        for a in self.container:
            if a.getStart() >= start and a.getEnd() <= end:
                subset.add(a)
        return subset

    def getOverlapping(self, annot):
        """
        Return a set of annotations from this set that overlap the
        annotation provided.
        """
        overlapping = AnnotationSet("overlapping")
        overlapping.addAll(self.getSubset(annot.getStart(), annot.getEnd()))
        return overlapping

    def getContainedSet(self, annot):
        subset = AnnotationSet("contained")
        for a in self.container:
            if annot.getStart() >= a.getStart()\
                    and annot.getEnd() <= a.getEnd():
                subset.add(a)
        return subset

    def getAnnotBySpan(self, start, end):
        """Return annotation that matches the given span."""
        for a in self.container:
            if start == a.getStart() and end == a.getEnd():
                return a
        return None

    def getAnnotByID(self, num):
        """Returns the annotation in the container that has the corresponding
        id number."""
        num=int(num)
        for a in self.container:
            if a.getID() == num:
                return a
        return None

    def getList(self):
        return self.container

    def get(self, i):
        """return the ith annot from the container"""
        if i > len(self.container):
            return None
        else:
            return self.container[i]

    def getNextAnnot(self, other):
        """Returns the next annotation in the container, otherwise None"""
        for a in self.container:
            if a.getStart() > other.getEnd():
                return a
        return None

    def getNextID(self):
        maxID = -1
        ids = [a.getID() for a in self.container]
        for i in ids:
            if i > maxID:
                maxID = i
        return maxID + 1

    def getPreviousAnnot(self, other):
        """returns the previous annotation."""
        prev = None
        for a in self.container:
            if a.getEnd() >= other.getStart():
                return prev
            prev = a
        return prev

    def extend(self, annotSet):
        """Extend this annotation set from another annotation set or list, with the given one."""
        for a in annotSet:
            self.add(a)

    def addAll(self, annot_list):
        """Adds all annotations from a list to the current annotation set."""
        for a in annot_list:
            self.add(a)

    def addPropBySpan(self, start, end, pname, prop):
        """Add a single property to the annot identified as being inside this span. """
        for a in self.container:
            if start >= a.getStart() and end <= a.getEnd():
                a.setProp(pname, prop)

    def addPropsBySpan(self, start, end, props):
        """Add props to the nps with the given span"""
        for a in self.container:
            if start == a.getStart() and end == a.getEnd():
                for p in props.keys():
                    a.setProp(p, props[p])

    def intersection(self, oset):
        """Returns the intersection between this set and the other """
        i = AnnotationSet("intersection of %s and %s" % (self.name, \
            oset.getName()))
        for a in self.container:
            if oset.contains(a):
                i.add(a)
        return i

    def fixIDs(self):
        """sometimes when adding multiple annot sets the ID orders get
        mangled"""
        i = 0
        for a in self.container:
            a.setProp("ID", i)
            a.setID(i)
            i+=1

