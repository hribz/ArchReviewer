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
        ret = '{\n'
        for child in self.children:
            ret = ret+child.__str__()+'\n'
        ret = ret + '}'
        return ret
    
class CppNode(Node):
    def __init__(self, tag, cond,loc):
        super(CppNode, self).__init__()
        self.cond = cond
        self.content = ''
        self.loc = loc
        self.tag = tag
    
    def __str__(self):
        ret = self.tag + ":" + str(self.loc) + "~" + str(self.endLoc)
        ret = ret + ' '
        if len(self.children) == 0:
            return ret
        return ret + super(CppNode, self).__str__()
    
    def add_content(self,content):
        self.content = content

# add new macro non exist in previous commit
TYPE_ADD = 0
# delete marco in previous commit
TYPE_DELETE = 1
# modify content in previous macro
TYPE_MODIFY = 2

class DiffNode(object):
    # in delete new_node is none
    # in add old_node is none
    def __init__(self,diff_type,old_node,new_node):
        self.diff_type = diff_type
        self.old_node = old_node
        self.new_node = new_node