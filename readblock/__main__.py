#   VIM SETTINGS: {{{3
#   VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
import sys
import argparse
import logging
import os 
import time
import pprint
import re
#   }}}1
import logging
import importlib
import importlib.resources
import pprint
import glob
from .readblock import ReadBlock
#   {{{2

_logging_format="%(funcName)s:%(levelname)s: %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format=_logging_format, datefmt=_logging_datetime)

__version__ = "0.0.0"

#   Include default values in help
_parser = argparse.ArgumentParser(description="Read taskblocks for tasklogs in given dir, output chosen items", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
_subparser = _parser.add_subparsers(dest="subparsers")

readblock = ReadBlock()

def _ArgsProcessFileList(_args):
#   {{{
    """If _args.infile is not None, return it, otherwise call readblock._GetFilesList_Monthly() with _args.(dir,prefix,postfix) and return result"""
    tasklog_files_list = []
    if (_args.infile is None):
        tasklog_files_list = readblock._GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
    else:
        if (_args.dir is not None):
            _log.warning("args.dir=(%s) ignored, recived infile=(%s)" % (str(_args.dir), str(_args.infile)))
        tasklog_files_list = _args.infile
    return tasklog_files_list
#   }}}

def _Interface_labels(_args):
#   {{{
    #_log.debug("args.infile=(%s)" % str(_args.infile))
    #tasklog_files_list = readblock._GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
    tasklog_files_list = _ArgsProcessFileList(_args)
    results_list = readblock.SearchTasklogs_DefaultSearchLabels(tasklog_files_list)
    for _results in results_list:
        if (_args.filenames):
            pass
        for loop_result_dict in _results:
            for k, v in loop_result_dict.items():
                print("%s: %s" % (str(k), str(v)))
#   }}}

def _Interface_startEndTime(_args):
#   {{{
    #_log.debug("args.infile=(%s)" % str(_args.infile))
    #tasklog_files_list = readblock._GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
    tasklog_files_list = _ArgsProcessFileList(_args)
    results_list = readblock.SearchTasklogs_DefaultSearchLabels(tasklog_files_list)
    for _results in results_list:
        if (_args.filenames):
            pass
        for loop_result_dict in _results:
            try:
                #   print either if '--both' is not given, or if both starttime and endtime are non-empty
                if not (_args.both) or (len(loop_result_dict['starttime'].strip()) > 0 and  len(loop_result_dict['timedone'].strip()) > 0):
                    print("%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone']))
            except Exception as e:
                pass
#   }}}

def _Interface_quality(_args):
#   {{{
    #_log.debug("args.infile=(%s)" % str(_args.infile))
    #if (_args.infile is None):
    #    tasklog_files_list = readblock._GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
    #else:
    #    tasklog_files_list = _args.infile
    tasklog_files_list = _ArgsProcessFileList(_args)
    results_list = readblock.SearchTasklogs_DefaultSearchLabels(tasklog_files_list)
    for _results in results_list:
        if (_args.filenames):
            pass
        for loop_result_dict in _results:
            try:
                print("%s\t%s\t%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone'], loop_result_dict['elapsed'], loop_result_dict['quality']))
            except Exception as e:
                pass
#   }}}

def _Interface_grabitems(_args):
#   {{{
    #_log.debug("args.infile=(%s)" % str(_args.infile))
    #tasklog_files_list = readblock._GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
    tasklog_files_list = _ArgsProcessFileList(_args)
    results_list = readblock.SearchTasklogs_grabitems(tasklog_files_list, _args.label)
    for _results in results_list:
        if (_args.filenames):
            pass
        for loop_result_dict in _results:
            #print(loop_result_dict)
            for k, v in loop_result_dict.items():
                if (_args.nokeys):
                    print(str(v))
                else:
                    print("%s: %s" % (str(k), str(v)))
#   }}}

def _Interface_todaytasks(_args):
#   {{{
    #_log.debug("args.infile=(%s)" % str(_args.infile))
    #tasklog_files_list = readblock._GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
    tasklog_files_list = _ArgsProcessFileList(_args)
    results_list = readblock.SearchTasklogs_todaytasks(tasklog_files_list)
    for _results in results_list:
        if (_args.filenames):
            pass
        for loop_result_dict in _results:
            try:
                print("%s\t%s" % (loop_result_dict['date'], loop_result_dict['todaytasks']))
            except Exception as e:
                pass
#   }}}

def _DirPath(arg_path):
#   {{{
    """Validate a given string exists as a directory"""
    if os.path.isdir(arg_path):
        return arg_path
    else:
        raise NotADirectoryError(arg_path)
#   }}}

def _FilePath(arg_path):
#   {{{
    """Validate a given string exists as a file"""
    if os.path.isfile(arg_path):
        return arg_path
    else:
        raise FileNotFoundError(arg_path) 
#   }}}


#   TODO: 2020-11-08T12:21:37AEDT Read regex from file - treatment of characters?
#   TODO: 2020-12-10T23:06:34AEDT option - get files matching mattern?
_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
_parser.add_argument('-v', '--debug', action='store_true', default=False)

_parser.add_argument('--gpgin', action='store_true', default=False, help="Input is gpg encrypted (decrypt with system gpg)")

#   dir, prefix, postfix -> get files in dir of the form '[prefix][yyyy]-[mm][postfix] from dir
_parser.add_argument('-D', '--dir', type=_DirPath, default=None, help="Path to dir containing tasklogs (exclusive with --infile)")
_parser.add_argument('--prefix', type=str, default=None, help="Tasklog filename before Y-m")
_parser.add_argument('--postfix', '-P', type=str, default=None, help="Tasklog filename after Y-m")

#   alternatively, specify file paths as arguments directly
_parser.add_argument('-F', '--infile', type=argparse.FileType('r'), action='append', help="Specify tasklog file(s) (exclusive with --dir)")


#   TODO: 2021-01-17T15:59:18AEDT return list-of-lists -> enabling us to distinguish what output belongs to what file, (and therefore include filename if given --filenames argument)
#   unimplemented:
_parser.add_argument('--filenames', action='store_true', default=False, help="Begin output for each file with file=(<filename>)")


_subparser_readlabels = _subparser.add_parser('labels', help="Print all taskblock label results")
_subparser_readlabels.set_defaults(func = _Interface_labels)

_subparser_startendtime = _subparser.add_parser('startendtime', help="Print start/end time for each taskblock")
_subparser_startendtime.set_defaults(func = _Interface_startEndTime)
_subparser_startendtime.add_argument('--both', action='store_true', default=False, help="Require both start and end time to print match")


_subparser_quality  = _subparser.add_parser('quality', help="Print start/end time, plus elapsed and timequality")
_subparser_quality.set_defaults(func = _Interface_quality)

_subparser_grabitems = _subparser.add_parser('grabitems', help="Print grab items, i.e: 'TODO: <datetime> <...>'")
_subparser_grabitems.set_defaults(func = _Interface_grabitems)
_subparser_grabitems.add_argument('-L', '--label', action='append', type=str, default=None, help="Search given label (otherwise use all defaults)")
_subparser_grabitems.add_argument('-n', '--nokeys', action='store_true', default=False, help="Do not include grab label with result")

_subparser_todaytasks = _subparser.add_parser('todaytasks', help="Get non-empty lines immediately after today-tasks")
_subparser_todaytasks.set_defaults(func = _Interface_todaytasks)


def cliscan():
    """Entry point for readtaskblocks"""
    _args = _parser.parse_args()
    #_log.debug("args=(%s)" % str(_args))

    #   TODO: 2021-01-17T16:04:57AEDT make '-F|--infile' exclusive with '-D|--dir' (and prefix/postfix)

    if (_args.debug):
        logging.getLogger().setLevel(logging.DEBUG)

    readblock.input_gpgin = _args.gpgin
    #regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = readblock._Read_Resources()

    if not hasattr(_args, 'func'):
        raise Exception("No subparser function")
    _args.func(_args)

#   call cliscan()
if __name__ == '__main__':
#   {{{
    cliscan()
#   }}}

#   }}}1
