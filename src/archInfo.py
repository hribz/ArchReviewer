import csv
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
__outputfile = "arch_info.json"

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
__macrofuncs = {}       # functional macros like: "GLIBVERSION(2,3,4)",
                        # used as "GLIBVERSION(x,y,z) 100*x+10*y+z"
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

def _flatten(l):
    """This function takes a list as input and returns a flatten version
    of the list. So all nested lists are unpacked and moved up to the
    level of the list."""
    i = 0
    while i < len(l):
        while isinstance(l[i], list):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i+1] = l[i]
        i += 1
    return l


def dictinvert(d):
    """This function inverses a dictionary that maps a key to a set of
    values into a dictionary that maps the values to the corresponding
    set of former keys."""
    inv = dict()
    for (k,v) in d.iteritems():
        for value in v:
            keys = inv.setdefault(value, [])
            keys.append(k)
    return inv


def _collectDefines(d):
    """This functions adds all defines to a set.
    e.g. #define FEAT_WIN
    also #define FEAT_WIN 12
    but not #define GLIBCVER(x,y,z) ...
    """
    __defset.add(d[0])
    if __defsetf.has_key(__curfile):
        __defsetf[__curfile].add(d[0])
    else:
        __defsetf[__curfile] = set([d[0]])
    return d


# possible operands:
#   - hexadecimal number
#   - decimal number
#   - identifier
#   - macro function, which is basically expanded via #define
#     to an expression
__numlitl = pypa.Literal('l').suppress() | pypa.Literal('L').suppress()
__numlitu = pypa.Literal('u').suppress() | pypa.Literal('U').suppress()

__string = pypa.QuotedString('\'', '\\')

__hexadec = \
        pypa.Literal('0x').suppress() + \
        pypa.Word(pypa.hexnums).\
        setParseAction(lambda t: str(int(t[0], 16))) + \
        pypa.Optional(__numlitu) + \
        pypa.Optional(__numlitl) + \
        pypa.Optional(__numlitl)

__integer = \
        pypa.Optional('~') + \
        pypa.Word(pypa.nums+'-').setParseAction(lambda t: str(int(t[0]))) + \
        pypa.Optional(pypa.Suppress(pypa.Literal('U'))) + \
        pypa.Optional(pypa.Suppress(pypa.Literal('L'))) + \
        pypa.Optional(pypa.Suppress(pypa.Literal('L')))

__identifier = \
        pypa.Word(pypa.alphanums+'_'+'-'+'@'+'$').setParseAction(_collectDefines)
__arg = pypa.Word(pypa.alphanums+'_')
__args = __arg + pypa.ZeroOrMore(pypa.Literal(',').suppress() + \
        __arg)
__fname = pypa.Word(pypa.alphas, pypa.alphanums + '_')
__function = pypa.Group(__fname + pypa.Literal('(').suppress() + \
        __args + pypa.Literal(')').suppress())


class NoEquivalentSigError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ("No equivalent signature found!")

class IfdefEndifMismatchError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ("Ifdef and endif do not match!")

##################################################


def _collapseSubElementsToList(node):
    """This function collapses all subelements of the given element
    into a list used for getting the signature out of an #ifdef-node."""
    # get all descendants - recursive - children, children of children ...
    itdesc = node.itertext()

    # iterate over the elemtents and add them to a list
    return ''.join([it for it in itdesc])


def _parseFeatureSignatureAndRewrite(sig):
    """This function parses a given feature-signature and rewrites
    the signature according to the given __pt mapping.
    """
    # this dictionary holds all transformations of operators from
    # the origin (cpp) to the compare (language)
    # e.g. in cpp && stands for the 'and'-operator.
    # the equivalent in maple (which is used for comparison)
    # is '&and'
    # if no equivalence can be found a name rewriting is done
    # e.g. 'defined'
    __pt = {
        #'defined' : 'defined_',
        'defined' : '',
        '!' : '&not',
        '&&': '&and',
        '||': '&or',
        '<' : '<',
        '>' : '>',
        '<=': '<=',
        '>=': '>=',
        '==': '=',
        '!=': '!=',
        '*' : '*',       # needs rewriting with parenthesis
        '/' : '/',
        '%' : '',        # needs rewriting a % b => modp(a, b)
        '+' : '+',
        '-' : '-',
        '&' : '',        # needs rewriting a & b => BitAnd(a, b)
        '|' : '',        # needs rewriting a | b => BitOr(a, b)
        '>>': '>>',      # needs rewriting a >> b => a / (2^b)
        '<<': '<<',      # needs rewriting a << b => a * (2^b)
    }

    def _rewriteOne(param):
        """This function returns each one parameter function
        representation for maple."""
        if param[0][0] == '!':
            ret = __pt[param[0][0]] + '(' + str(param[0][1]) + ')'
        if param[0][0] == 'defined':
            ret = __pt[param[0][0]] + str(param[0][1])
        return  ret


    def _rewriteTwo(param):
        """This function returns each two parameter function
        representation for maple."""
        # rewriting rules
        if param[0][1] == '%':
            return 'modp(' + param[0][0] + ',' + param[0][2] + ')'

        ret = ' ' + __pt[param[0][1]] + ' '
        ret = '(' + ret.join(map(str, param[0][0::2])) + ')'

        if param[0][1] in ['<', '>', '<=', '>=', '!=', '==']:
            ret = '(true &and ' + ret + ')'
        return ret

    operand = __string | __hexadec | __integer | \
            __function | __identifier
    compoperator = pypa.oneOf('< > <= >= == !=')
    calcoperator = pypa.oneOf('+ - * / & | << >> %')
    expr = pypa.operatorPrecedence(operand, [
        ('defined', 1, pypa.opAssoc.RIGHT, _rewriteOne),
        ('!',  1, pypa.opAssoc.RIGHT, _rewriteOne),
        (calcoperator, 2, pypa.opAssoc.LEFT, _rewriteTwo),
        (compoperator, 2, pypa.opAssoc.LEFT, _rewriteTwo),
        ('&&', 2, pypa.opAssoc.LEFT, _rewriteTwo),
        ('||', 2, pypa.opAssoc.LEFT, _rewriteTwo),
    ])

    try:
        rsig = expr.parseString(sig)[0]
    except pypa.ParseException, e:
        print('ERROR (parse): cannot parse sig (%s) -- (%s)' %
                (sig, e.col))
        return sig
    except RuntimeError:
        print('ERROR (time): cannot parse sig (%s)' % (sig))
        return sig
    except ValueError, e:
        print('ERROR (parse): cannot parse sig (%s) ~~ (%s)' %
                (sig, e))
        return sig
    return ''.join(rsig)


def _getMacroSignature(ifdefnode):
    """This function gets the signature of an ifdef or corresponding macro
    out of the xml-element and its descendants. Since the macros are held
    inside the xml-representation in an own namespace, all descendants
    and their text corresponds to the macro-signature.
    """
    # get either way the expr-tag for if and elif
    # or the name-tag for ifdef and ifndef,
    # which are both the starting point for signature
    # see the srcml.dtd for more information
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


def _prologCSV(folder, file, headings, delimiter = ","):
    """prolog of the CSV-output file
    no corresponding _epilogCSV."""
    fd = open(os.path.join(folder, file), 'w')
    fdcsv = csv.writer(fd, delimiter=delimiter)
    fdcsv.writerow(["sep=" + delimiter])
    fdcsv.writerow(headings)
    return (fd, fdcsv)


def _parseAndAddDefine(node):
    """This function extracts the identifier and the corresponding
    expansion from define macros. Later on these are used in conditionals
    in order to make them comparable."""
    define = _collapseSubElementsToList(node)

    # match only macro functions, no macro objects
    anytext = pypa.Word(pypa.printables)
    macrodef = pypa.Literal('#define').suppress() + __function + anytext

    try:
        res = macrodef.parseString(define)
    except pypa.ParseException:
        return

    iden = ''.join(map(str, res[0]))
    expn = res[-1]
    para = res[1:-1]
    __macrofuncs[iden] = (para, expn)


def _getArchInfo(root):
    node_stack = []
    parcon = False
    parend = False

    for event, elem in etree.iterwalk(root, events=("start", "end")):
        ns, tag = __cpprens.match(elem.tag).groups()

        if ((tag in __conditionals_all)
                and (event == 'start')
                and (ns == __cppnscpp)):
            parcon = True

        if ((tag in __conditionals_all)
                and (event == 'end')
                and (ns == __cppnscpp)):
            parcon = False

            if ((tag in __conditionals_else)
                    or (tag in __conditionals_elif)):
                pass

        # hitting end-tag of elif-macro
        if ((tag in __conditionals_elif)
                and (event == 'end')
                and (ns == __cppnscpp)):
            parcon = False

        # hitting end-tag of define-macro
        if ((tag in __macro_define) \
                and (event == 'end') \
                and (ns == __cppnscpp)):
            _parseAndAddDefine(elem)

        # iterateting in subtree of conditional-node
        if parcon:
            continue

        # handling endif-macro
        # hitting an endif-macro start-tag
        if ((tag in __conditionals_endif) \
                and (event == "start") \
                and (ns == __cppnscpp)):    # check the cpp:namespace
            parend = True

        # hitting the endif-macro end-tag
        if ((tag in __conditionals_endif) \
                and (event == "end") \
                and (ns == __cppnscpp)):    # check the cpp:namespace
            parend = False

        # iterating the endif-node subtree
        if parend:
            continue

    if (node_stack):
        raise IfdefEndifMismatchError()
    return 


def _getNumOfDefines(defset):
    """This method returns the number of defines, that have the following
    structure:
    #define FEAT_A
    #define FEAT_B 5
    Both defines are macro-objects. macro-functions like the following
    are not considered.
    #define CHECKVERSION(x,y,z) x*100+y*10+z
    All determined elements are derived from the ifdef macros.
    """
    # basic operation of this function is to check __defset against
    # __macrofuncs
    funcmacros = __macrofuncs.keys()
    funcmacros = map(lambda n: n.split('(')[0], funcmacros)
    funcmacros = set(funcmacros)

    return len((defset - funcmacros))


def resetModule() :
    global __defset, __defsetf
    __defset = set()        # macro-objects
    __defsetf = dict()      # macro-objects per file


def apply(folder, options):
    resetModule()

    # outputfile
    fd, fdcsv = _prologCSV(os.path.join(folder, os.pardir), __outputfile, __statsorder.__members__.keys())

    global __curfile
    fcount = 0
    files = returnFileNames(folder, ['.xml'])
    files.sort()
    ftotal = len(files)

    for file in files:
        __curfile = file

        try:
            tree = etree.parse(file)
        except etree.XMLSyntaxError:
            print("ERROR: cannot parse (%s). Skipping this file." % os.path.join(folder, file))
            continue

        root = tree.getroot()
        try:
            (features, _, featuresgrouter) = _getArchInfo(root)
        except IfdefEndifMismatchError:
            print("ERROR: ifdef-endif mismatch in file (%s)" % (os.path.join(folder, file)))
            continue

        print(__defset)

        # file successfully parsed
        fcount += 1
        print('INFO: parsing file (%5d) of (%5d) -- (%s).' % (fcount, ftotal, os.path.join(folder, file)))

        # collect arch info


        #adjust file name if wanted
        if options.filenamesRelative : # relative file name (root is project folder (not included in path))
            file = os.path.relpath(file, folder)

        if options.filenames == options.FILENAME_SRCML : # cppstats file names
            pass # nothing to do here, as the file path is the cppstats path by default
        if options.filenames == options.FILENAME_SOURCE : # source file name
            file = file.replace(".xml", "").replace("/_cppstats/", "/source/", 1)


    fd.close()


def getResultsFile():
    return __outputfile

