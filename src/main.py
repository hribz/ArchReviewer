import os
import sys
import shutil  # for copying files and folders
import errno  # for error/exception handling
import threading  # for parallelism
import subprocess  # for calling other commands
import re  # for regular expressions
from abc import ABCMeta, abstractmethod  # abstract classes
#import pynotify  # for system notifications
from argparse import ArgumentParser, RawTextHelpFormatter  # for parameters to this script
from collections import OrderedDict  # for ordered dictionaries
import tempfile # for temporary files

# #################################################
# imports from subfolders

# import different kinds of analyses
import xmlGen, analysis

def processFile(infile, outfile, options):

    tmpfile = tempfile.mkstemp(suffix=".xml")[1] # temporary srcML file

    # xmlGen
    options.infile = infile
    options.outfile = tmpfile
    xmlGen.processFile(options.infile, options)

    # analysis
    options.infile = tmpfile
    options.outfile = outfile
    analysis.processFile(options.infile, options)

    # delete temp file
    os.remove(tmpfile)


def getOptions():
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    default_file = "input.txt"


    inputgroup = parser.add_mutually_exclusive_group(required=False)  # TODO check if True is possible some time...
    inputgroup.add_argument("--file", type=str, dest="inputfile", nargs=2, metavar=("IN", "OUT"), default=default_file, const=default_file,
                            help="a source file IN that is prepared and analyzed, the analysis results are written to OUT"
                                    "\n(--list is the default)")

    options = parser.parse_args()
    return options

def main():
    options = getOptions()


    if (options.inputfile):
        options.infile = os.path.normpath(os.path.abspath(options.inputfile[0])) # IN
        options.outfile = os.path.normpath(os.path.abspath(options.inputfile[1])) # OUT

        # check if inputfile exists
        if (not os.path.isfile(options.infile)):
            print "ERROR: input file '{}' cannot be found!".format(options.infile)
            sys.exit(1)

        processFile(options.infile, options.outfile, options)

    else:
        print "This should not happen! No input file or list of projects given!"
        sys.exit(1)

if __name__ == '__main__':
    main()
