# Class defined for containing reconcile annotations
#
class Annotation:
    def __init__(self, s, e, i, a, t):
        self.start = int(s)
        self.end = int(e)
        self.id = int(i)
        self.attr = a
        self.text = t

    def __len__(self):
        return len(self.text)

    #emulates lists
    def __getitem__(self, prop):
        return self.attr.get(prop, "")

    def __setitem__(self, prop, value):
        self.attr[prop] = value

    def setStart(self, s):
        self.start = int(s)

    def setEnd(self, e):
        self.start = int(e)

    def setATTR(self, a):
        self.attr = a

    def getATTR(self, prop):
        return self.attr.get(prop, "")

    def hasProp(self, s):
        if s in self.attr.keys():
            return True
        return False

    def setProp(self, s, p):
        self.attr[s] = p

    def setID(self, i):
        self.id = int(i)

    def setText(self, t):
        self.text = t

    def getStart(self):
        return int(self.start)

    def getSpan(self):
        return (self.start, self.end)

    def getEnd(self):
        return int(self.end)

    def getProps(self):
        return self.attr

    def addProps(self, props):
        for p in props.keys():
            self.attr[p] = props[p]

    def getText(self):
        return self.text

    def getPNText(self):
        start = self.attr.get("contains_pn", (0, 0))[0]
        end = self.attr.get("contains_pn", (0, 0))[1]
        return self.text[start:end]

    def setREF(self, ref):
        self.attr["REF"] = str(ref)

    def getREF(self):
        return int(self.attr.get("REF", -1))

    def getID(self):
        return int(self.id)

    def contains(self, other):
        if (self.start <= other.start) and (self.end >= other.end):
            return True
        else:
            return False

    def __cmp__(self, other):
        if self.start < other.start:
            if self.end > other.end:
                return 1
            else:
                return -1
        elif self.start == other.start:
            if self.end < other.end:
                return -1
            elif self.end > other.end:
                return 1
            else:
                return 0
        else:
            return 1

    def getProps2String(self):
        s = ""
        for key in self.attr.keys():
            #don't print empty REFs
            if key == "REF" and self.attr["REF"] == "":
                continue
            s += "\t%s=\"%s\"" % (key, self.attr[key])
        return s

    def pprint(self):
        return "%s" % self.text.replace("\n"," ")

    def ppprint(self):
        if self.attr.get("TEXT_CLEAN", None) is not None:
            txt = self.attr["TEXT_CLEAN"]
        else:
            txt = self.text.replace("\n", " ")

        return "%s (%d,%d)" % (txt, self.start, self.end)

    def pppprint(self):
        return "[%d] %s [%s] (%d,%d)" % (self.id, self.text.replace("\n",""),
                self.attr.get("MIN",""), self.start, self.end)

    def __str__(self):
        s = self.getProps2String()
        return "%d %s (%d,%d) %s" % (self.id, self.text, self.start,
                self.end, s)

