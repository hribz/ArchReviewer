import os
import sys
import shutil  # for copying files and folders
import errno  # for error/exception handling
import subprocess  # for calling other commands
import re  # for regular expressions
from abc import ABCMeta, abstractmethod  # abstract classes
from collections import OrderedDict


# #################################################
# paths

import xmlTrans

def getPreparationScript(filename):
    return os.path.join(os.path.dirname(xmlTrans.__file__), filename)


# #################################################
# imports from subfolders

import cli

# for rewriting of #ifdefs to "if defined(..)"
# for turning multiline macros to oneliners
# for deletion of include guards in H files
from xmlTrans import rewriteMultilineMacros

# #################################################
# global constants

_filepattern_c = ('.c', '.C')
_filepattern_h = ('.h', '.H')
_filepattern = _filepattern_c + _filepattern_h

_cvs_pattern = (".git", ".cvs", ".svn")


# #################################################
# helper functions

def notify(message):
    pass

    # import pynotify  # for system notifications
    #
    # pynotify.init("ArchReviewer")
    # notice = pynotify.Notification(message)
    # notice.show()


# function for ignore pattern
def filterForFiles(dirpath, contents, pattern=_filepattern):
    filesToIgnore = [filename for filename in contents if
                     not filename.endswith(pattern) and
                     not os.path.isdir(os.path.join(dirpath, filename))
                     ]
    foldersToIgnore = [dir for dir in contents if
                       dir in _cvs_pattern and
                       os.path.isdir(os.path.join(dirpath, dir))
                       ]
    return filesToIgnore + foldersToIgnore


def runBashCommand(command, shell=False, stdin=None, stdout=None):
    # split command if not a list/tuple is given already
    if type(command) is str:
        command = command.split()

    process = subprocess.Popen(command, shell=shell, stdin=stdin, stdout=stdout, stderr=stdout)
    out, err = process.communicate()  # TODO do something with the output
    process.wait()

    # FIXME do something with return value of process.wait()!
    # if ret is not 0:
    #     print "#### " + " ".join(command) + " returned " + str(ret)


def replaceMultiplePatterns(replacements, infile, outfile):
    with open(infile, "rb") as source:
        with open(outfile, "w") as target:
            data = source.read()
            for pattern, replacement in replacements.iteritems():
                data = re.sub(pattern, replacement, data, flags=re.MULTILINE)
            target.write(data)


def stripEmptyLinesFromFile(infile, outfile):
    with open(infile, "rb") as source:
        with open(outfile, "w") as target:
            for line in source:
                if line.strip():
                    target.write(line)


def silentlyRemoveFile(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured


def src2srcml(src, srcml):
    __s2sml = "srcml"
    runBashCommand([__s2sml, src, "--language=C"], stdout=open(srcml, 'w+'))  # + " -o " + srcml)
    # FIXME incorporate "|| rm ${f}.xml" from bash


def srcml2src(srcml, src):
    __sml2s = "srcml"
    runBashCommand([__sml2s, srcml], stdout=open(src, 'w+'))  # + " -o " + src)


# #################################################
# abstract preparation thread

class AbstractPreparationThread(object):
    '''This class prepares a single folder according to the given kind of preparations in an independent thread.'''
    __metaclass__ = ABCMeta
    sourcefolder = "source"

    def __init__(self, options, inputfolder=None, inputfile=None):
        self.options = options
        self.notrunnable = False

        if (inputfolder):
            self.file = None
            self.folder = inputfolder
            self.source = os.path.join(self.folder, self.sourcefolder)

            self.project = os.path.basename(self.folder)

            # get full path of subfolder "_ArchReviewer"
            self.subfolder = os.path.join(self.folder, self.getSubfolder())

        elif (inputfile):
            self.file = inputfile
            self.outfile = self.options.outfile
            self.folder = os.path.dirname(self.file)

            self.project = os.path.basename(self.file)

            # get full path of temp folder for
            import tempfile
            self.subfolder = tempfile.mkdtemp(suffix=self.getSubfolder())


        else:
            self.notrunnable = True

    def startup(self):
        # LOGGING
        notify("starting '" + self.getPreparationName() + "' preparations:\n " + self.project)
        print "# starting '" + self.getPreparationName() + "' preparations: " + self.project

    def teardown(self):

        # delete temp folder for file-based preparation
        if (self.file):
            shutil.rmtree(self.subfolder)

        # LOGGING
        notify("finished '" + self.getPreparationName() + "' preparations:\n " + self.project)
        print "# finished '" + self.getPreparationName() + "' preparations: " + self.project

    def run(self):

        if (self.notrunnable):
            print "ERROR: No single file or input list of projects given!"
            return

        self.startup()

        if (self.file):

            self.currentFile = os.path.join(self.subfolder, self.project)
            shutil.copyfile(self.file, self.currentFile)

            self.backupCounter = 0
            self.prepareFile()

            shutil.copyfile(self.currentFile + ".xml", self.outfile)
        else:
            # copy C and H files to self.subfolder
            self.copyToSubfolder()
            # preparation for all files in the self.subfolder (only C and H files)
            for root, subFolders, files in os.walk(self.subfolder):
                for file in files:
                    f = os.path.join(root, file)
                    self.currentFile = f

                    self.backupCounter = 0
                    self.prepareFile()

        self.teardown()

    def copyToSubfolder(self):

        # TODO debug
        # echo '### preparing sources ...'
        # echo '### copying all-files to one folder ...'

        # delete folder if already existing
        if os.path.isdir(self.subfolder):
            shutil.rmtree(self.subfolder)

        # copy all C and H files recursively to the subfolder
        shutil.copytree(self.source, self.subfolder, ignore=filterForFiles)

    def backupCurrentFile(self):
        '''# backup file'''
        if (not self.options.nobak):
            bak = self.currentFile + ".bak" + str(self.backupCounter)
            shutil.copyfile(self.currentFile, bak)
            self.backupCounter += 1

    @classmethod
    @abstractmethod
    def getPreparationName(cls):
        pass

    @abstractmethod
    def getSubfolder(self):
        pass

    @abstractmethod
    def prepareFile(self):
        pass

    # TODO refactor such that file has not be opened several times! (__currentfile)
    def rewriteMultilineMacros(self):
        tmp = self.currentFile + "tmp.txt"

        self.backupCurrentFile()  # backup file

        # turn multiline macros to oneliners
        shutil.move(self.currentFile, tmp)  # move for script
        rewriteMultilineMacros.translate(tmp, self.currentFile)  # call function

        os.remove(tmp)  # remove temp file


    def deleteWhitespace(self):
        """deletes leading, trailing and inter (# ... if) whitespaces,
        replaces multiple whitespace with a single space"""
        tmp = self.currentFile + "tmp.txt"

        self.backupCurrentFile()  # backup file

        # replace patterns with replacements
        replacements = {
            '^[ \t]+': '',  # leading whitespaces
            '[ \t]+$': '',  # trailing whitespaces
            '#[ \t]+': '#',  # inter (# ... if) whitespaces # TODO '^#[ \t]+' or '#[ \t]+'
            '\t': ' ',  # tab to space
            '[ \t]{2,}': ' '  # multiple whitespace to one space

        }
        replaceMultiplePatterns(replacements, self.currentFile, tmp)

        # move temp file to output file
        shutil.move(tmp, self.currentFile)


    def transformFileToSrcml(self):
        source = self.currentFile
        dest = self.currentFile + ".xml"

        # transform to srcml
        src2srcml(source, dest)


# #################################################
# preparation-thread implementations

class ArchInfoPreparationThread(AbstractPreparationThread):
    @classmethod
    def getPreparationName(cls):
        return "archinfo"

    def getSubfolder(self):
        return "_ArchReviewer"

    def prepareFile(self):
        # multiline macros
        self.rewriteMultilineMacros()

        # delete leading, trailing and inter (# ... if) whitespaces
        self.deleteWhitespace()

        # transform file to srcml
        self.transformFileToSrcml()


# #################################################
# collection of preparation threads

# add all subclass of AbstractPreparationThread as available preparation kinds
__preparationkinds = []
for cls in AbstractPreparationThread.__subclasses__():
    entry = (cls.getPreparationName(), cls)
    __preparationkinds.append(entry)

# exit, if there are no preparation threads available
if (len(__preparationkinds) == 0):
    print "ERROR: No preparation tasks found! Revert your changes or call the maintainer."
    print "Exiting now..."
    sys.exit(1)
__preparationkinds = OrderedDict(__preparationkinds)


def getKinds():
    return __preparationkinds


# #################################################
# main method


def applyFile(kind, inputfile, options):
    kinds = getKinds()

    # get proper preparation thread and call it
    threadClass = kinds[kind]
    thread = threadClass(options, inputfile=inputfile)
    thread.run()


def getFoldersFromInputListFile(inputlist):
    ''' This method reads the given inputfile line-wise and returns the read lines without line breaks.'''

    file = open(inputlist, 'r')  # open input file
    folders = file.read().splitlines()  # read lines from file without line breaks
    file.close()  # close file

    folders = filter(lambda f: not f.startswith("#"), folders)  # remove commented lines
    folders = filter(os.path.isdir, folders)  # remove all non-directories
    folders = map(os.path.normpath, folders)  # normalize paths for easier transformations

    # TODO log removed folders

    return folders


def applyFolders(kind, inputlist, options):
    kinds = getKinds()

    # get the list of projects/folders to process
    folders = getFoldersFromInputListFile(inputlist)

    # for each folder:
    for folder in folders:
        # start preparations for this single folder

        # get proper preparation thread and call it
        threadClass = kinds[kind]
        thread = threadClass(options, inputfolder=folder)
        thread.run()


def applyFoldersAll(inputlist, options):
    kinds = getKinds()
    for kind in kinds.keys():
        applyFolders(kind, inputlist, options)
