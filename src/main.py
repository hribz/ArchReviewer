import os
import sys
#import pynotify  # for system notifications
from argparse import ArgumentParser, RawTextHelpFormatter  # for parameters to this script
from collections import OrderedDict  # for ordered dictionaries
import tempfile # for temporary files
import cli, xmlTrans.xmlGen as xmlGen, analysis


# #################################################
# version number

__version__ = "Beta"

def version() :
    return "archReviewer " + __version__


# #################################################
# collection of analyses

# add all kinds of analyses: (name -> (xmlGen, analysis))
__kinds = []
__kinds.append(('archinfo', ('archinfo', 'archinfo')))


# exit, if there are no analysis threads available
if (len(__kinds) == 0) :
    print "ERROR: No analyses available! Revert your changes or call the maintainer."
    print "Exiting now..."
    sys.exit(1)

__kinds = OrderedDict(__kinds)


# #################################################
# main method


def applyFile(kind, infile, outfile, options):

    tmpfile = tempfile.mkstemp(suffix=".xml")[1] # temporary srcML file

    # xmlGen
    options.infile = infile
    options.outfile = tmpfile
    xmlGen.applyFile(kind, options.infile, options)

    # analysis
    options.infile = tmpfile
    options.outfile = outfile
    analysis.applyFile(kind, options.infile, options)

    # delete temp file
    os.remove(tmpfile)

def applyFolders(option_kind, inputlist, options):
    kind = __kinds.get(option_kind)
    xmlGenKind = kind[0]
    analysisKind = kind[1]

    xmlGen.applyFolders(xmlGenKind, inputlist, options)
    analysis.applyFolders(analysisKind, inputlist, options)

def applyFoldersAll(inputlist, options):
    for kind in __kinds.keys():
        applyFolders(kind, inputlist, options)


def main():
    # #################################################
    # options parsing

    options = cli.getOptions(__kinds, step = cli.steps.ALL)

    # #################################################
    # main

    if (options.inputfile):

        # split --file argument
        options.infile = os.path.normpath(os.path.abspath(options.inputfile[0])) # IN
        options.outfile = os.path.normpath(os.path.abspath(options.inputfile[1])) # OUT

        # check if inputfile exists
        if (not os.path.isfile(options.infile)):
            print "ERROR: input file '{}' cannot be found!".format(options.infile)
            sys.exit(1)

        applyFile(options.kind, options.infile, options.outfile, options)

    elif (options.inputlist):
        # handle --list argument
        options.inputlist = os.path.normpath(os.path.abspath(options.inputlist)) # LIST

        # check if list file exists
        if (not os.path.isfile(options.inputlist)):
            print "ERROR: input file '{}' cannot be found!".format(options.inputlist)
            sys.exit(1)

        if (options.allkinds):
            applyFoldersAll(options.inputlist, options)
        else:
            applyFolders(options.kind, options.inputlist, options)

    else:
        print "This should not happen! No input file or list of projects given!"
        sys.exit(1)

if __name__ == '__main__':
    main()
