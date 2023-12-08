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

##################################################
# config:
__outputfile = "arch_info_result.json"

# error numbers:
__errorfexp = 0
__errormatch = []
##################################################


##################################################
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


class NoEquivalentSigError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ("No equivalent signature found!")

class IfdefEndifMismatchError(Exception):
    def __init__(self, loc, msg=""):
        self.loc=loc
        self.msg=msg
        pass
    def __str__(self):
        return ("Ifdef and endif do not match! (loc: %s, msg: %s)")

##################################################


def _collapseSubElementsToList(node):
    """This function collapses all subelements of the given element
    into a list used for getting the signature out of an #ifdef-node."""
    # get all descendants - recursive - children, children of children ...
    itdesc = node.itertext()

    # iterate over the elemtents and add them to a list
    return ''.join([it for it in itdesc])


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


def buildCppTree(root):
    global __cpp_root
    __cpp_root = CppNode('root', '', -1)
    node_stack = [__cpp_root]

    for event, elem in etree.iterwalk(root, events=("start", "end")):
        ns, tag = __cpprens.match(elem.tag).groups()
        src_line = elem.sourceline-1

        if ((tag in __conditionals_all) and (event == 'start') and (ns == __cppnscpp)):
            cond_str = __getCondStr(elem)
            for event_, operand in etree.iterwalk(elem, events=("start", "end")):
                ns_, tag_ = __cpprens.match(operand.tag).groups()
                if ((tag_ in ['name']) and (event_ == 'start')):
                    try:
                        __identifier.parseString(operand.text)[0]
                    except pypa.ParseException:
                        print('ERROR (parse): cannot parse cond_str (%s) -- (%s)' %
                            (cond_str, src_line))
            if (tag in __conditionals):
                cond_node = CondNode()
                node_stack[-1].add_child(cond_node)
                cpp_node = CppNode(tag, cond_str, src_line)
                cond_node.add_child(cpp_node)
                node_stack.append(cpp_node)
            elif ((tag in __conditionals_else)
                    or (tag in __conditionals_elif)):
                cond_node = node_stack[-1].parent
                cpp_node = CppNode(tag, cond_str, src_line)
                cond_node.add_child(cpp_node)
                node_stack.pop()
                node_stack.append(cpp_node)

        if ((tag in __macro_define) and (event == 'end') and (ns == __cppnscpp)):
            pass

        if ((tag in __conditionals_endif) and (event == "start") and (ns == __cppnscpp)):
            if (len(node_stack)==1):
                raise IfdefEndifMismatchError(src_line)
            node_stack.pop().parent.endifLoc = src_line

    if (len(node_stack)!=1):
        raise IfdefEndifMismatchError(-1)
    __cpp_root.verify()
    return 


def analysisPass(folder, options, first):
    global __old_tree_root, __new_tree_root
    resetModule()

    # outputfile
    fd = open(os.path.join(folder, __outputfile), 'w')

    global __curfile
    fcount = 0
    files = returnFileNames(folder, ['.xml'])
    files.sort()
    ftotal = len(files)

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
            buildCppTree(root)
        except IfdefEndifMismatchError as e:
            print("ERROR: ifdef-endif mismatch in file (%s:%s msg: %s)" % (os.path.join(folder, file), e.loc, e.msg))
            continue
        
        print(__defsetf[__curfile])
        print(__cpp_root)

        # collect arch info
        if first:
            __old_tree_root = __cpp_root

        else:
            __new_tree_root = __cpp_root

        #adjust file name if wanted
        if options.filenamesRelative : # relative file name (root is project folder (not included in path))
            file = os.path.relpath(file, folder)

        if options.filenames == options.FILENAME_SRCML : # ArchReviewer file names
            pass # nothing to do here, as the file path is the ArchReviewer path by default
        if options.filenames == options.FILENAME_SOURCE : # source file name
            file = file.replace(".xml", "").replace("/_ArchReviewer/", "/source/", 1)


    fd.close()

def resetModule() :
    global __defset, __defsetf
    __defset = set()        # macro-objects
    __defsetf = dict()      # macro-objects per file


def apply(folder, options):
    analysisPass(folder, options, True)

def addCommandLineOptionsMain(optionparser):
    ''' add command line options for a direct call of this script'''
    optionparser.add_argument("--folder", dest="folder",
        help="input folder [default=%(default)s]", default=".")


def addCommandLineOptions(optionparser) :
    pass

def getResultsFile():
    return __outputfile

