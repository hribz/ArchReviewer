import archInfo

class Node(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.confirmed = False
        self.endLoc = -1

    def __str__(self):
        ret = '['
        for child in self.children:
            ret = ret+child.__str__()
        ret = ret + ']'
        return ret

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def verify(self):
        if self.endLoc == -1:
            raise archInfo.IfdefEndifMismatchError(self.loc, "line of #endif error")
        for child in self.children:
            child.verify()

class CondNode(Node):
    def __init__(self, loc):
        super(CondNode, self).__init__()
        self.loc = loc

    def __str__(self):
        ret = '{'
        for child in self.children:
            ret = ret+child.__str__()
        ret = ret + '}'
        return ret
    
class CppNode(Node):
    def __init__(self, tag, cond, loc):
        super(CppNode, self).__init__()
        self.cond = cond
        self.loc = loc
        self.tag = tag
    
    def __str__(self):
        ret = self.tag + ":" + str(self.loc) + self.cond
        ret = ret + ' '
        if len(self.children) == 0:
            return ret
        return ret + super(CppNode, self).__str__()