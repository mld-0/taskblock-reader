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

def Read_Resources():
    resource_regexfile_taskblocklabels = [ "readblock", "regexfile-taskblockLabels.txt" ]
    resource_regexfile_beginStartEnd = [ "readblock", "regexfile-beginStartEnd.txt" ]
    resource_grab_labels = [ "readblock", "grab-labels.txt" ]
    #   Read resource files
    regex_search_labels_list = []
    regex_lines_beginStartEnd_list = []
    _grab_labels_default = []
    #   {{{
    path_regexfile_taskblocklabels = None
    regex_str = None
    with importlib.resources.path(*resource_regexfile_taskblocklabels) as p:
        path_regexfile_taskblocklabels = str(p)
    try:
        with open(path_regexfile_taskblocklabels, 'r') as f:
            regex_str = f.read()
    except Exception as e:
        _log.error("%s, %s" % (type(e), str(e)))
        raise Exception("Failed to read path_regexfile_taskblocklabels=(%s)" % str(path_regexfile_taskblocklabels))
    for loop_line in regex_str.split('\n'):
        regex_search_labels_list.append(loop_line)
    path_regexfile_beginStartEnd = None
    regex_str = None
    with importlib.resources.path(*resource_regexfile_beginStartEnd) as p:
        path_regexfile_beginStartEnd = str(p)
    try:
        with open(path_regexfile_beginStartEnd, 'r') as f:
            regex_str = f.read()
    except Exception as e:
        _log.error("%s, %s" % (type(e), str(e)))
        raise Exception("Failed to read path_regexfile_beginStartEnd=(%s)" % str(path_regexfile_beginStartEnd))
    for loop_line in regex_str.split('\n'):
        regex_lines_beginStartEnd_list.append(loop_line)
    path_grab_labels = None
    with importlib.resources.path(*resource_grab_labels) as p:
        path_grab_labels = str(p)
    try:
        with open(path_grab_labels) as f:
            for loop_line in f:
                #loop_grablabel = _grab_label_prefix + loop_line.strip() + _grab_label_postfix
                loop_grablabel = CombineGrabLabelRegex(loop_line.strip())
                _grab_labels_default.append(loop_grablabel)
    except Exception as e:
        _log.error("%s, %s" % (type(e), str(e)))
        raise Exception("Failed to read path_grab_labels=(%s)" % str(path_grab_labels))
    #   }}}
    return [ regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default ] 



#def _Interface_labels(_args):
#    regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = Read_Resources()
#    tasklog_files_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
#    for loop_tasklog in tasklog_files_list:
#        if (input_gpgin):
#            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
#        else:
#            loop_tasklog_stream = open(loop_tasklog, "r")
#        if (_args.filenames):
#            loop_tasklog_basename = os.path.basename(loop_tasklog)
#            print("file=(%s)" % str(loop_tasklog_basename))
#        _results = readblock.ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
#        for loop_result_dict in _results:
#            for k, v in loop_result_dict.items():
#                print("%s: %s" % (str(k), str(v)))
#        loop_tasklog_stream.close()
#
#def _Interface_startEndTime(_args):
#    regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = Read_Resources()
#    tasklog_files_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
#    for loop_tasklog in tasklog_files_list:
#        if (input_gpgin):
#            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
#        else:
#            loop_tasklog_stream = open(loop_tasklog, "r")
#        if (_args.filenames):
#            loop_tasklog_basename = os.path.basename(loop_tasklog)
#            print("file=(%s)" % str(loop_tasklog_basename))
#        _results = readblock.ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
#        for loop_result_dict in _results:
#            try:
#                print("%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone']))
#            except Exception as e:
#                pass
#        loop_tasklog_stream.close()
#
#def _Interface_quality(_args):
#    regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = Read_Resources()
#    tasklog_files_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
#    for loop_tasklog in tasklog_files_list:
#        if (input_gpgin):
#            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
#        else:
#            loop_tasklog_stream = open(loop_tasklog, "r")
#        if (_args.filenames):
#            loop_tasklog_basename = os.path.basename(loop_tasklog)
#            print("file=(%s)" % str(loop_tasklog_basename))
#
#        _results = readblock.ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
#        for loop_result_dict in _results:
#            try:
#                print("%s\t%s\t%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone'], loop_result_dict['elapsed'], loop_result_dict['quality']))
#            except Exception as e:
#                pass
#        loop_tasklog_stream.close()
#
#def _Interface_grabitems(_args):
#    regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = Read_Resources()
#    tasklog_files_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
#    for loop_tasklog in tasklog_files_list:
#        if (input_gpgin):
#            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
#        else:
#            loop_tasklog_stream = open(loop_tasklog, "r")
#        if (_args.filenames):
#            loop_tasklog_basename = os.path.basename(loop_tasklog)
#            print("file=(%s)" % str(loop_tasklog_basename))
#
#        #_log.debug("_grab_labels=(%s)" % str(_grab_labels))
#        _results = None
#        if (_args.label is None):
#            _results = readblock.SearchStreamLineByLine(loop_tasklog_stream, _grab_labels_default)
#        else:
#            _grab_labels = []
#            _log.debug("_args.label=(%s)" % str(_args.label))
#            for loop_label in _args.label:
#                loop_grablabel = CombineGrabLabelRegex(loop_label)
#                _grab_labels.append(loop_grablabel)
#            _log.debug("_grab_labels=(%s)" % str(_grab_labels))
#
#            _results = readblock.SearchStreamLineByLine(loop_tasklog_stream, _grab_labels)
#        for loop_result_dict in _results:
#            #print(loop_result_dict)
#            for k, v in loop_result_dict.items():
#                if (_args.nokeys):
#                    print(str(v))
#                else:
#                    print("%s: %s" % (str(k), str(v)))
#        loop_tasklog_stream.close()
#
#def _Interface_todaytasks(_args):
#    regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = Read_Resources()
#    tasklog_files_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)
#    for loop_tasklog in tasklog_files_list:
#        if (input_gpgin):
#            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
#        else:
#            loop_tasklog_stream = open(loop_tasklog, "r")
#        if (_args.filenames):
#            loop_tasklog_basename = os.path.basename(loop_tasklog)
#            print("file=(%s)" % str(loop_tasklog_basename))
#        _regex_startday = r"^======== StartDay:"
#        _regex_todaytasks = [ r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})", r"(?P<todaytasks>Today-Tasks:\s*\n(.*\n)+)" ]
#
#        _results = readblock.ScanGetNonEmptyLineRange(loop_tasklog_stream, _regex_startday, _regex_todaytasks, regex_lines_beginStartEnd_list)
#        for loop_result_dict in _results:
#            try:
#                print("%s\t%s" % (loop_result_dict['date'], loop_result_dict['todaytasks']))
#            except Exception as e:
#                pass
#        loop_tasklog_stream.close()

def _DirPath(string):
#   {{{
    """Validate a given string exists as a directory"""
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)
#   }}}

def _GetFilesList_Monthly(arg_dir, arg_prefix, arg_postfix):
#   {{{
    """Get all files in a given dir matching 'arg_prefix + [0-9]{4}-[0-9]{2} + arg_postfix'"""
    regex_str_monthly = "[0-9][0-9][0-9][0-9]-[0-9][0-9]"
    glob_filename_str = ""
    if (arg_prefix is not None):
        glob_filename_str += arg_prefix
    glob_filename_str += regex_str_monthly 
    if (arg_postfix is not None):
        glob_filename_str += arg_postfix
    #if (arg_extension is not None):
    #    glob_filename_str += "." + arg_extension
    if (arg_dir is None):
        _log.error("need -D DIR plus --prefix PREFIX or --postfix POSTFIX")
        sys.exit(2)
    if (arg_prefix is None and arg_postfix is None):
        _log.error("need -D DIR plus --prefix PREFIX or --postfix POSTFIX")
        sys.exit(2)
    _log.debug("arg_dir=(%s)" % str(arg_dir))
    _log.debug("glob_filename_str=(%s)" % str(glob_filename_str))
    glob_filepath_str = os.path.join(arg_dir, glob_filename_str)
    _log.debug("glob_filepath_str=(%s)" % str(glob_filepath_str))
    results_list = glob.glob(glob_filepath_str)
    results_list.sort()
    _log.debug("results_list:\n%s" % pprint.pformat(results_list))
    return results_list
#   }}}

def CombineGrabLabelRegex(arg_label):
#   {{{
    """Create 'grabblock' search regex from label, label may be preceded only by non-word chars excluding newline, and followed by ':', capture group name is the label with s/\W/_/g"""
    _grab_label_prefix = r"^[^\w\n]*"
    _grab_label_postfix = r": "
    _capturegroup_Label = re.sub(r"\W", "_", arg_label)
    regex_result = _grab_label_prefix + arg_label + _grab_label_postfix + r"(?P<" + _capturegroup_Label + r">.*)$"
    _log.debug("regex_result=(%s)" % str(regex_result))
    return regex_result
#   }}}

#   TODO: 2020-11-08T12:21:37AEDT Read regex from file - treatment of characters?
#   TODO: 2020-12-10T23:06:34AEDT option - get files matching mattern?
_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
_parser.add_argument('-v', '--debug', action='store_true', default=False)

#   dir, prefix, postfix -> get files in dir of the form '[prefix][yyyy]-[mm][postfix]
_parser.add_argument('-D', '--dir', type=_DirPath, help="Path to dir containing tasklogs")
_parser.add_argument('--prefix', type=str, default=None, help="Tasklog filename before Y-m")
_parser.add_argument('--postfix', '-P', type=str, default=None, help="Tasklog filename after Y-m")
_parser.add_argument('-F', '--filenames', action='store_true', default=False, help="Begin output for each file with file=(<filename>)")

_subparser_readlabels = _subparser.add_parser('labels', help="Print all taskblock label results")
#_subparser_readlabels.set_defaults(func=_Interface_labels)

_subparser_startendtime = _subparser.add_parser('startendtime', help="Print start/end time for each taskblock")
#_subparser_startendtime.set_defaults(func=_Interface_labels)


_subparser_quality  = _subparser.add_parser('quality', help="Print start/end time, plus elapsed and timequality")
#_subparser_quality.set_defaults(func=_Interface_quality)

_subparser_grabitems = _subparser.add_parser('grabitems', help="Print grab items, i.e: 'TODO: <datetime> <...>'")
#_subparser_grabitems.set_defaults(func=_Interface_grabitems)
_subparser_grabitems.add_argument('-L', '--label', action='append', type=str, default=None, help="Search given label (otherwise use all defaults)")
_subparser_grabitems.add_argument('-n', '--nokeys', action='store_true', default=False, help="Do not include grab label with result")

_subparser_todaytasks = _subparser.add_parser('todaytasks', help="Get non-empty lines immediately after today-tasks")
#_subparser_todaytasks.set_defaults(func=_Interface_todaytasks)

readblock = ReadBlock()
input_gpgin = True




def cliscan():
    """Entry point for readtaskblocks"""
    _args = _parser.parse_args()
    #_log.debug("args=(%s)" % str(_args))

    if (_args.debug):
        logging.getLogger().setLevel(logging.DEBUG)


    regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = Read_Resources()

    #_args.func(_args)

    tasklog_files_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)

    #   TODO: 2021-01-12T19:22:08AEDT function for each subparser
    for loop_tasklog in tasklog_files_list:
        #   Decrypt to stream, or open as stream (decrypted streams are stored in memory)
        if (input_gpgin):
            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
        else:
            loop_tasklog_stream = open(loop_tasklog, "r")

        if (_args.filenames):
            loop_tasklog_basename = os.path.basename(loop_tasklog)
            print("file=(%s)" % str(loop_tasklog_basename))

        #if (_args.subparsers == 'labels'):
        #    _results = readblock.ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
        #    for loop_result_dict in _results:
        #        for k, v in loop_result_dict.items():
        #            print("%s: %s" % (str(k), str(v)))

        if (_args.subparsers == 'startendtime'):
            _results = readblock.ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
            for loop_result_dict in _results:
                try:
                    print("%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone']))
                except Exception as e:
                    pass

        if (_args.subparsers == 'quality'):
            _results = readblock.ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
            for loop_result_dict in _results:
                try:
                    print("%s\t%s\t%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone'], loop_result_dict['elapsed'], loop_result_dict['quality']))
                except Exception as e:
                    pass

        if (_args.subparsers == 'grabitems'):
            #_log.debug("_grab_labels=(%s)" % str(_grab_labels))
            _results = None
            if (_args.label is None):
                _results = readblock.SearchStreamLineByLine(loop_tasklog_stream, _grab_labels_default)
            else:
                _grab_labels = []
                _log.debug("_args.label=(%s)" % str(_args.label))
                for loop_label in _args.label:
                    loop_grablabel = CombineGrabLabelRegex(loop_label)
                    _grab_labels.append(loop_grablabel)
                _log.debug("_grab_labels=(%s)" % str(_grab_labels))
                _results = readblock.SearchStreamLineByLine(loop_tasklog_stream, _grab_labels)
            for loop_result_dict in _results:
                #print(loop_result_dict)
                for k, v in loop_result_dict.items():
                    if (_args.nokeys):
                        print(str(v))
                    else:
                        print("%s: %s" % (str(k), str(v)))

        if (_args.subparsers == 'todaytasks'):
            _regex_startday = r"^======== StartDay:"
            _regex_todaytasks = [ r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})", r"(?P<todaytasks>Today-Tasks:\s*\n(.*\n)+)" ]
            _results = readblock.ScanGetNonEmptyLineRange(loop_tasklog_stream, _regex_startday, _regex_todaytasks, regex_lines_beginStartEnd_list)
            for loop_result_dict in _results:
                try:
                    print("%s\t%s" % (loop_result_dict['date'], loop_result_dict['todaytasks']))
                except Exception as e:
                    pass

        #loop_tasklog_stream.close()

#   call cliscan()
if __name__ == '__main__':
#   {{{
    cliscan()
#   }}}

#   }}}1
