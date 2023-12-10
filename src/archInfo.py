import os
import re
import sys

 # python-lxml module
from lxml import etree
# pyparsing module
import pyparsing as pypa
pypa.ParserElement.enablePackrat() # speed up parsing
sys.setrecursionlimit(8000)        # handle larger expressions
from cpp_tree import *
import json

##################################################
# config:
__outputfile = "arch_info_result.json"

# constants:
# namespace-constant for src2srcml
__cppnscpp = 'http://www.srcML.org/srcML/cpp'
__cppnsdef = 'http://www.srcML.org/srcML/src'
__cpprens = re.compile('{(.+)}(.+)')

# conditionals - necessary for parsing the right tags
__conditionals = ['if', 'ifdef', 'ifndef']
__conditionals_elif = ['elif']
__conditionals_else = ['else']
__conditionals_endif = ['endif']
__conditionals_all = __conditionals + __conditionals_elif + \
        __conditionals_else
__macro_define = ['define']
__curfile = ''          # current processed xml-file
__defset = set()        # macro-objects
__defsetf = dict()      # macro-objects per file


##################################################
# helper functions, constants and errors
def returnFileNames(folder, extfilt = ['.xml']):
    '''This function returns all files of the input folder <folder>
    and its subfolders.'''
    filesfound = list()

    if os.path.isdir(folder):
        wqueue = [os.path.abspath(folder)]

        while wqueue:
            currentfolder = wqueue[0]
            wqueue = wqueue[1:]
            foldercontent = os.listdir(currentfolder)
            tmpfiles = filter(lambda n: os.path.isfile(
                    os.path.join(currentfolder, n)), foldercontent)
            tmpfiles = filter(lambda n: os.path.splitext(n)[1] in extfilt,
                    tmpfiles)
            tmpfiles = map(lambda n: os.path.join(currentfolder, n),
                    tmpfiles)
            filesfound += tmpfiles
            tmpfolders = filter(lambda n: os.path.isdir(
                    os.path.join(currentfolder, n)), foldercontent)
            tmpfolders = map(lambda n: os.path.join(currentfolder, n),
                    tmpfolders)
            wqueue += tmpfolders

    return filesfound


def _collectDefines(d):
    if d[0]=='defined':
        return
    __defset.add(d[0])
    if __defsetf.has_key(__curfile):
        __defsetf[__curfile].add(d[0])
    else:
        __defsetf[__curfile] = set([d[0]])
    return d

__identifier = \
        pypa.Word(pypa.alphanums+'_'+'-'+'@'+'$').setParseAction(_collectDefines)


class IfdefEndifMismatchError(Exception):
    def __init__(self, loc, msg=""):
        self.loc=loc
        self.msg=msg
        pass
    def __str__(self):
        return ("Ifdef and endif do not match! (loc: %s, msg: %s)")

##################################################

def __getCondStr(ifdefnode):
    """
    return the condition source code of condition directive
    """
    nexpr = []
    res = ''
    _, tag = __cpprens.match(ifdefnode.tag).groups()

    # get either the expr or the name tag,
    # which is always the second descendant
    if (tag in ['if', 'elif', 'ifdef', 'ifndef']):
        nexpr = [itex for itex in ifdefnode.iterdescendants()]
        if (len(nexpr) == 1):
            res = nexpr[0].tail
        else:
            nexpr = nexpr[1]
            res = ''.join([token for token in nexpr.itertext()])
    return res

def findMacroNameInDb(macro_name, db):
    for arch_name, arch_dict in db.items():
        if 'macro_names' in arch_dict:
            if macro_name in arch_dict.get('macro_names'):
                return str(arch_name)
    return None

def buildCppTree(root, db):
    global __cpp_root, __line_and_arch
    __line_and_arch = dict()
    __cpp_root = CppNode('root', '', -1)
    __cpp_root.endLoc = 0
    node_stack = [__cpp_root]

    for event, elem in etree.iterwalk(root, events=("start", "end")):
        ns, tag = __cpprens.match(elem.tag).groups()
        src_line = elem.sourceline-1

        if ((tag in __conditionals_all) and (event == 'start') and (ns == __cppnscpp)):
            cond_str = __getCondStr(elem)
            arch_names = set()
            # print(elem)
            for event_, operand in etree.iterwalk(elem, events=("start", "end")):
                ns_, tag_ = __cpprens.match(operand.tag).groups()
                if ((tag_ in ['name']) and len(operand)==0 and (event_ == 'start')):
                    try:
                        macro_name = __identifier.parseString(operand.text)[0]
                    except pypa.ParseException:
                        print('ERROR (parse): cannot parse cond_str (%s) -- (%s)' %
                            (cond_str, src_line))
                    else:
                        arch_name = findMacroNameInDb(macro_name, db)
                        if arch_name:
                            arch_names.add(arch_name)

            if (tag in __conditionals): # #if #ifdef #ifndef
                cond_node = CondNode(src_line)
                node_stack[-1].add_child(cond_node)
                cpp_node = CppNode(tag, cond_str, src_line)
                cond_node.add_child(cpp_node)
                node_stack.append(cpp_node)
            else: # #elif #else
                cond_node = node_stack[-1].parent
                cpp_node = CppNode(tag, cond_str, src_line)
                cond_node.add_child(cpp_node)
                node_stack.pop().endLoc=src_line-1
                node_stack.append(cpp_node)

            if arch_names:
                __line_and_arch[cpp_node] = arch_names

        if ((tag in __macro_define) and (event == 'end') and (ns == __cppnscpp)):
            pass

        if ((tag in __conditionals_endif) and (event == "start") and (ns == __cppnscpp)):
            if (len(node_stack)==1):
                print(__cpp_root)
                raise IfdefEndifMismatchError(src_line, '#endif not match')
            lastCppNode = node_stack.pop()
            lastCppNode.endLoc = src_line-1
            lastCppNode.parent.endLoc = src_line

    if (len(node_stack)!=1):
        raise IfdefEndifMismatchError(-1)
    __cpp_root.verify()
    return 


def analysisPass(folder, db, first):
    global __old_tree_root, __new_tree_root
    resetModule()

    # outputfile
    fd = open(os.path.join(folder, __outputfile), 'w')

    global __curfile
    fcount = 0
    files = returnFileNames(folder, ['.xml'])
    files.sort()
    ftotal = len(files)
    json_result = {}

    for file in files:
        __curfile = file
        if not __defsetf.has_key(__curfile):
            __defsetf[__curfile] = set()
        fcount += 1
        print('INFO: parsing file (%5d) of (%5d) -- (%s).' % (fcount, ftotal, os.path.join(folder, file)))

        try:
            tree = etree.parse(file)
        except etree.XMLSyntaxError:
            print("ERROR: cannot parse (%s). Skipping this file." % os.path.join(folder, file))
            continue

        root = tree.getroot()
        try:
            buildCppTree(root, db)
        except IfdefEndifMismatchError as e:
            print("ERROR: ifdef-endif mismatch in file (%s:%s msg: %s)" % (os.path.join(folder, file), e.loc, e.msg))
            continue
        
        # print(__defsetf[__curfile])

        if __line_and_arch:
            json_data = {}
            
            for node in __line_and_arch.keys():
                json_data[node.loc] = dict()
                json_data[node.loc][node.endLoc] = list(__line_and_arch[node])
            # print(__cpp_root)

            file = os.path.relpath(file, folder)
            file, ext = os.path.splitext(file)
            json_result[file] = json_data

    json.dump(json_result, fd, indent=2)
    fd.close()

def resetModule() :
    global __defset, __defsetf
    __defset = set()        # macro-objects
    __defsetf = dict()      # macro-objects per file


def apply(folder, db):
    analysisPass(folder, db, True)

def addCommandLineOptionsMain(optionparser):
    ''' add command line options for a direct call of this script'''
    optionparser.add_argument("--folder", dest="folder",
        help="input folder [default=%(default)s]", default=".")


def addCommandLineOptions(optionparser) :
    pass

def getResultsFile():
    return __outputfile

