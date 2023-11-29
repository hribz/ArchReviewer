import os
import sys
import shutil  # for copying files and folders
import errno  # for error/exception handling
import threading  # for parallelism
import subprocess  # for calling other commands
import re  # for regular expressions
from abc import ABCMeta, abstractmethod  # abstract classes
from argparse import ArgumentParser, RawTextHelpFormatter  # for parameters to this script
from collections import OrderedDict  # for ordered dictionaries


class AbstractAnalysisThread(object):
    '''This class analyzes a whole project according to the given kind of analysis in an independent thread.'''
    __metaclass__ = ABCMeta

    def __init__(self, options, inputfolder=None, inputfile=None):
        self.options = options
        self.notrunnable = False

        if (inputfolder):
            self.file = None
            self.folder = os.path.join(inputfolder, self.getPreparationFolder())
            self.project = os.path.basename(self.folder)

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
        notify("starting '" + self.getName() + "' analysis:\n " + self.project)
        print "# starting '" + self.getName() + "' analysis: " + self.project

    def teardown(self):

        # delete temp folder for file-based preparation
        if (self.file):
            shutil.rmtree(self.tmpfolder)

        # LOGGING
        notify("finished '" + self.getName() + "' analysis:\n " + self.project)
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


# #################################################
# analysis-thread implementations

class GeneralAnalysisThread(AbstractAnalysisThread):
    @classmethod
    def getName(cls):
        return "general"

    @classmethod
    def getPreparationFolder(self):
        return "_cppstats"

    @classmethod
    def getResultsFile(self):
        return general.getResultsFile()

    @classmethod
    def addCommandLineOptions(cls, optionParser):
        title = "Options for analysis '" + cls.getName() + "'"
        group = optionParser.add_argument_group(title.upper())
        general.addCommandLineOptions(group)

    def analyze(self, folder):
        general.process(folder, self.options)


# #################################################
# main method


def processFile(kind, inputfile, options):
    thread = threadClass(options, inputfile=inputfile)
    thread.run()
