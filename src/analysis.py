import os
import sys
import shutil  # for copying files and folders
from abc import ABCMeta, abstractmethod  # abstract classes
from argparse import ArgumentParser, RawTextHelpFormatter  # for parameters to this script
from collections import OrderedDict  # for ordered dictionaries
import json
import archInfo


# #################################################
# abstract analysis thread

class AbstractAnalysisThread(object):
    '''This class analyzes a whole project according to the given kind of analysis in an independent thread.'''
    __metaclass__ = ABCMeta

    def __init__(self, options, inputfolder=None, inputfile=None):
        self.options = options
        self.notrunnable = False
        with open('tools/arch_info.json', 'r') as f:
            self.arch_info_db = json.load(f)

        if (inputfolder):
            self.file = None
            self.folder = os.path.join(inputfolder, self.getPreparationFolder())
            self.project = os.path.basename(self.folder)
            self.old_commit_folder = os.path.join(self.folder, "old_commit")
            self.new_commit_folder = os.path.join(self.folder, "new_commit")

        elif (inputfile):
            self.file = inputfile
            self.outfile = self.options.outfile
            self.project = os.path.basename(self.file)

            # get full path of temp folder for
            import tempfile
            tmpfolder = tempfile.mkdtemp(suffix=self.getPreparationFolder())
            self.tmpfolder = tmpfolder
            self.folder = os.path.join(tmpfolder, self.getPreparationFolder())
            os.makedirs(self.folder)  # create the folder actually

            self.resultsfile = os.path.join(self.tmpfolder, self.getResultsFile())

        else:
            self.notrunnable = True


    def startup(self):
        # LOGGING
        print "# starting '" + self.getName() + "' analysis: " + self.project

    def teardown(self):

        # delete temp folder for file-based preparation
        if (self.file):
            shutil.rmtree(self.tmpfolder)

        # LOGGING
        print "# finished '" + self.getName() + "' analysis: " + self.project

    def run(self):

        if (self.notrunnable):
            print "ERROR: No single file or input list of projects given!"
            return

        self.startup()

        # copy srcml inputfile to tmp folder again and analyze project there!
        if (self.file):
            currentFile = os.path.join(self.folder, self.project)
            if (not currentFile.endswith(".xml")):
                currentFile += ".xml"
            shutil.copyfile(self.file, currentFile)

        # for all files in the self.folder (only C and H files)
        self.analyze(self.folder)

        # copy main results file from tmp folder to destination, if given
        if (self.file and self.resultsfile != self.outfile):
            shutil.copyfile(self.resultsfile, self.outfile)

        self.teardown()

    @classmethod
    @abstractmethod
    def getName(cls):
        pass

    @classmethod
    @abstractmethod
    def getPreparationFolder(self):
        pass

    @classmethod
    @abstractmethod
    def getResultsFile(self):
        pass

    @classmethod
    @abstractmethod
    def addCommandLineOptions(cls, optionParser):
        pass

    @abstractmethod
    def analyze(self):
        pass


class ArchInfoAnalysisThread(AbstractAnalysisThread):
    @classmethod
    def getName(cls):
        return "archinfo"

    @classmethod
    def getPreparationFolder(self):
        return "_ArchReviewer"

    @classmethod
    def getResultsFile(self):
        return archInfo.getResultsFile()

    @classmethod
    def addCommandLineOptions(cls, optionParser):
        title = "Options for analysis '" + cls.getName() + "'"
        group = optionParser.add_argument_group(title.upper())
        archInfo.addCommandLineOptions(group)

    def analyze(self, folder):
        archInfo.apply(folder, self.arch_info_db)


# #################################################
# collection of analysis threads

# add all subclass of AbstractAnalysisThread as available analysis kinds
__analysiskinds = []
for cls in AbstractAnalysisThread.__subclasses__():
    entry = (cls.getName(), cls)
    __analysiskinds.append(entry)

# exit, if there are no analysis threads available
if (len(__analysiskinds) == 0):
    print "ERROR: No analysis tasks found! Revert your changes or call the maintainer."
    print "Exiting now..."
    sys.exit(1)

__analysiskinds = OrderedDict(__analysiskinds)


def getKinds():
    return __analysiskinds


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
    folders = map(os.path.normpath, folders) # normalize paths for easier transformations

    #TODO log removed folders

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
