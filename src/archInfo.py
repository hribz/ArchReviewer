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
import difflib
import copy

##################################################
# config:
__outputfile = "arch_info_result.json"
__backendfile = "result_for_backend.json"

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
__function_call = ['call']
__include_file = ['include']
__comment = ['comment']
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

def findIntrinsicsInDb(intrinsics, db):
    for arch_name, arch_dict in db.items():
        if 'intrinsics' in arch_dict:
            if intrinsics in arch_dict.get('intrinsics'):
                return str(arch_name)
    return None

def findIncludeNameInDb(include, db):
    for arch_name, arch_dict in db.items():
        if 'include_file_name' in arch_dict:
            if include in arch_dict.get('include_file_name'):
                return str(arch_name)
    return None

def write_content(lines,cppnode):
    if isinstance(cppnode,CppNode) and cppnode.loc > 0 and cppnode.endLoc > 0:
        content = ''
        if cppnode.loc == cppnode.endLoc:
            content = lines[cppnode.loc-1]
        else:#multi line
            for i in range(cppnode.loc,cppnode.endLoc+1):
                content += lines[i-1]
        cppnode.add_content(content)

def buildCppTree(source,root, db):
    global  __line_and_arch, __line_and_intrinsics, __line_and_include, __line_and_comment
    __line_and_arch = dict()
    __line_and_intrinsics = dict()
    __line_and_include = dict()
    __line_and_comment = dict()
    __cpp_root = CppNode('root', '', -1)
    __cpp_root.endLoc = 0
    node_stack = [__cpp_root]
    comment_stack = []
    source_file = open(source.replace('.xml',''),'r')
    lines = source_file.readlines()
    
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
                node = node_stack.pop()
                node.endLoc=src_line-1
                write_content(lines,node)
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
            write_content(lines,lastCppNode)
            lastCppNode.parent.endLoc = src_line
            write_content(lines,lastCppNode.parent)

        if ((tag in __function_call) and (event == 'start') and (ns == __cppnsdef)):
            for event_, operand in etree.iterwalk(elem, events=("start", "end")):
                ns_, tag_ = __cpprens.match(operand.tag).groups()
                if ((tag_ in ['name']) and len(operand)==0 and (event_ == 'start')):
                    intrinsics = findIntrinsicsInDb(operand.text, db)
                    if intrinsics:
                        if not __line_and_intrinsics.has_key(src_line):
                            __line_and_intrinsics[src_line] = list()
                        __line_and_intrinsics[src_line].append(intrinsics)
                    break

        if ((tag in __include_file) and (event == 'start') and (ns == __cppnscpp)):
            for event_, operand in etree.iterwalk(elem, events=("start", "end")):
                ns_, tag_ = __cpprens.match(operand.tag).groups()
                if ((tag_ in ['file']) and len(operand)==0 and (event_ == 'start')):
                    # print(operand.text[1:-1])
                    include = findIncludeNameInDb(operand.text[1:-1], db)
                    if include:
                        if not __line_and_include.has_key(src_line):
                            __line_and_include[src_line] = list()
                        __line_and_include[src_line].append(include)
                    break
        
        if ((tag in __comment)):
            comment_type = elem.get('type')
            comment_content = elem.text.strip()
            if comment_type == 'line':
                __line_and_comment[src_line] = {'type':'line', 'line_e':src_line, 'content': comment_content}
            elif comment_type == 'block':
                if event == 'start':
                    __line_and_comment[src_line] = {'type':'block', 'line_e':src_line, 'content': comment_content}
                    comment_stack.append(__line_and_comment[src_line])
                else:
                    (comment_stack.pop())['line_e']=src_line

    if (len(node_stack)!=1):
        raise IfdefEndifMismatchError(-1)
    __cpp_root.verify()
    return copy.deepcopy(__cpp_root)

def __line_has_change(line_b, line_e, diff_lines):
    '''
    [line_b, line_e] ∩ diff_lines
    diff_lines format: [[line1], [line2,line3], ...]
    return format: True/False, ["line1", "line2-line3] 
    '''
    ret = []
    flag = False
    for integers in diff_lines:
        if len(integers)==1:
            lb = le = integers[0]
        elif len(integers)==2:
            lb = integers[0]
            le = integers[1]
        else:
            print(f'diff lines error {diff_lines}')
            continue

        if le<line_b:
            continue
        if lb>line_e:
            break
        lb = max(line_b, integers[0])
        le = min(line_e, integers[1])
        if (lb==le):
            ret.append(str(lb))
        else:
            ret.append(str(lb)+'-'+str(le))
    return flag, ret

def __str2line(input_string):
    matches = re.findall(r'\d+', input_string)
    return [int(match) for match in matches]

def analysisPass(folder, db, git_diff):
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
    result_to_backend = {}
    result_to_backend['detail'] = {}
    result_arch = set()

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
            buildCppTree(file,root, db)
        except IfdefEndifMismatchError as e:
            print("ERROR: ifdef-endif mismatch in file (%s:%s msg: %s)" % (os.path.join(folder, file), e.loc, e.msg))
            continue
        
        # print(__defsetf[__curfile])

        file = os.path.relpath(file, folder)
        file, ext = os.path.splitext(file)
        json_data = {}
        arch_line = []
        comments = {}
        
        if __line_and_arch:
            for node in __line_and_arch.keys():
                json_data[str(node.loc) + ',' + str(node.endLoc)] = list(__line_and_arch[node])

                flag, diff_line = __line_has_change(node.loc, node.endLoc, git_diff[file])
                if flag:
                    result_arch = result_arch.union(__line_and_arch[node])
                    arch_line.extend(diff_line)
            # print(__cpp_root)
                
        if __line_and_include:
            # print(__line_and_intrinsics)
            for line in __line_and_include.keys():
                if not json_data.has_key(str(line) + ',' + str(line)):
                    json_data[str(line) + ',' + str(line)] = list(__line_and_include[line])
                else:
                    json_data[str(line) + ',' + str(line)].extend(__line_and_include[line])
                
                flag, diff_line = __line_has_change(line, line, git_diff[file])
                if flag:
                    result_arch = result_arch.union(__line_and_include[line])
                    arch_line.extend(diff_line)

        if __line_and_intrinsics:
            # print(__line_and_intrinsics)
            for line in __line_and_intrinsics.keys():
                if not json_data.has_key(str(line) + ',' + str(line)):
                    json_data[str(line) + ',' + str(line)] = list(__line_and_intrinsics[line])
                else:
                    json_data[str(line) + ',' + str(line)].extend(__line_and_intrinsics[line])

                flag, diff_line = __line_has_change(line, line, git_diff[file])
                if flag:
                    result_arch = result_arch.union(__line_and_include[line])
                    arch_line.extend(diff_line)
        
        if __line_and_comment:
            for line in __line_and_comment.keys():
                comment = __line_and_comment[line]
                comment_split_by_line = comment['content'].splitlines()
                flag, diff_line = __line_has_change(line, comment['line_e'], git_diff[file])
                if flag:
                    for comment_line in diff_line:
                        integers = __str2line(comment_line)
                        if len(integers)==1:
                            comment_lb = comment_le = integers[0]-line
                        else:
                            comment_lb = integers[0]-line
                            comment_le = integers[1]-line
                        comments[comment_line] = '\n'.join(comment_split_by_line[comment_lb:comment_le+1])

        if json_data:
            json_result[file] = json_data
        
        if arch_line:
            result_to_backend['detail'][file] = dict()
            result_to_backend['detail'][file]['arch_line'] = arch_line
            result_to_backend['detail'][file]['comments'] = comments

    json.dump(json_result, fd, indent=2)
        
    if result_arch:
        result_to_backend['result'] = ','.join(result_arch)
    parent_directory = os.path.abspath(os.path.join(folder, os.pardir))
    with open(os.path.join(parent_directory, __backendfile), 'w') as f:
        json.dump(result_to_backend, f, indent=2)
        
    fd.close()

def dfs(current_node,macro_dict,macro_list):
    for child_node in current_node.children:
        if child_node.endLoc != -1:
            key = str(child_node.loc) + '~' + str(child_node.endLoc)
            macro_dict[key] = child_node
            macro_list.append((child_node.loc,child_node.endLoc))
        dfs(child_node,macro_dict,macro_list)

def generate_dict(root):
    macro_dict = dict()
    line_range_list = list()
    if root.endLoc != -1:
        key = str(root.loc)+'~'+str(root.endLoc)
        macro_dict[key] = root
        line_range_list.append((root.loc,root.endLoc))
    dfs(root,macro_dict,line_range_list)
    return macro_dict,line_range_list

def node_contain(macro_list,macro_dict,index):
    for start,end in macro_list:
        if index >= start and index <= end:
            key = str(start)+'~'+str(end)
            node = macro_dict[key]
            if len(node.children)!=0:
                continue
            else:
                return True,macro_dict[key]
    return False,None
        
# only analias one file in different commit
def diffAnalias(old_commit_dir,new_commit_dir,filename,db):
    resetModule()
    
    old_path = os.path.join(old_commit_dir,filename)
    new_path = os.path.join(new_commit_dir,filename)
    
    try:
        old_tree = etree.parse(old_path)
    except etree.XMLSyntaxError:
        print("ERROR: cannot parse (%s). Skipping this file." % old_path)

    try:
        new_tree = etree.parse(new_path)
    except etree.XMLSyntaxAssertionError:
        print("ERROR: cannot parse (%s). Skipping this file." % old_path)
    
    old_root = old_tree.getroot()
    new_root = new_tree.getroot()
    
    try:
        old_cpp = buildCppTree(old_path,old_root,db)
    except IfdefEndifMismatchError as e:
        print("ERROR: ifdef-endif mismatch in file (%s:%s msg: %s)" % (old_path, e.loc, e.msg))
    try:
        new_cpp = buildCppTree(new_path, new_root,db)
    except IfdefEndifMismatchError as e:
        print("ERROR: ifdef-endif mismatch in file (%s:%s msg: %s)" % (new_path, e.loc, e.msg))
    
    diff_list = []
    # old_macro_dict = generate_dict(old_cpp)
    new_macro_dict,new_macro_list = generate_dict(new_cpp)
    
    old_lines = open(old_path.replace(".xml",""),'r').readlines()
    new_lines = open(new_path.replace(".xml",""),'r').readlines()
    diff = difflib.unified_diff(old_lines,new_lines)
    
    for line in diff:
        if line[:2] in ["@@","--","++"]:
            continue
        if line[0] == '-':# left only
            row_line = line[1:]
            file_line = old_lines.index(row_line)
            
        elif line[0] == '+':# new commit only
            row_line = line[1:]
            file_line = new_lines.index(row_line)+1
            flag,node = node_contain(new_macro_list,new_macro_dict,file_line)
            if flag:
                diff_list.append(node)
    
    
    return diff_list

def resetModule() :
    global __defset, __defsetf
    __defset = set()        # macro-objects
    __defsetf = dict()      # macro-objects per file


def apply(folder, db, git_diff):
    analysisPass(folder, db, git_diff)

def addCommandLineOptionsMain(optionparser):
    ''' add command line options for a direct call of this script'''
    optionparser.add_argument("--folder", dest="folder",
        help="input folder [default=%(default)s]", default=".")


def addCommandLineOptions(optionparser) :
    pass

def getResultsFile():
    return __outputfile

