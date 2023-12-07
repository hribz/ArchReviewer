class Node:
    def __init__(self):
        self.parent = None
        self.children: list[Node] = []
        self.confirmed = False

    def __str__(self) -> str:
        ret = '['
        for child in self.children:
            ret = ret+child.__str__()
        ret = ret + ']'
        return ret

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

class CondNode(Node):
    def __init__(self):
        """条件编译结构树的Cond节点, 代表源代码中出现的一个完整的条件编译结构
        注: Cond节点在parser解析到#if时创建, 表示该#if控制的条件编译结构, 其父节点和子节点一定为Cpp节点

        """
        super().__init__()

    def __str__(self) -> str:
        ret = '{'
        for child in self.children:
            ret = ret+child.__str__()
        ret = ret + '}'
        return ret

class CppNode(Node):
    def __init__(self, tag: str, cond: str, loc=None):
        """条件编译结构树的Cpp节点, 代表源代码中出现的#if, #elif等条件编译指令

        :param tag: 节点类型标签("#if"等)
        :param cond: 条件编译指令对应的条件源码
        :param loc: 条件编译指令对应的源代码行号
        """
        super().__init__()
        self.cond = cond
        if loc is not None:
            self.loc = loc
        self.tag = tag
    
    def __str__(self) -> str:
        ret = self.tag + ":" + str(self.loc) + self.cond
        ret = ret + ' '
        if len(self.children) == 0:
            return ret
        return ret + super().__str__()