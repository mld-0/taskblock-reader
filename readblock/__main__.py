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
#import reader_tasklogTaskBlocks.readblock as readblock
import importlib
import importlib.resources
import pprint
import glob
from .readblock import ReadBlock
#   {{{2
__version__ = "0.0.0"

#   Usage:
#>%     python run-taskblock-reader.py --infile /Users/mldavis/Dropbox/_TaskLogs/_worklog/2020-12.worklog.vimgpg
#   Only works with tasklogs new enough to use the format of that given in the file,
#   crashes on older files (those with no matches at all?)

_logging_format="%(funcName)s:%(levelname)s: %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

#path_home = os.path.expanduser("~")
#path_templates_dir = os.path.join(path_home, "_templates")
#path_regex_str = os.path.join(path_templates_dir, "tasklog-taskblock-asregex.txt")

path_regex_str= None
with importlib.resources.path("readblock", "regexfile-taskblock.txt") as p:
    path_regex_str = str(p)
    _log.debug("path_regex_str=(%s)" % str(path_regex_str))

#   Include default values in help
_parser = argparse.ArgumentParser(description="Read line(s) in file beginning with specified labels in groups", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
_subparser = _parser.add_subparsers(dest="subparsers")

def _DirPath(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def _GetFilesList_Monthly(arg_dir, arg_prefix, arg_postfix):
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
    #results_list.sort(reverse=True)
    results_list.sort()
    _log.debug("results_list:\n%s" % pprint.pformat(results_list))
    return results_list


#   TODO: 2020-11-08T12:21:37AEDT Read regex from file - treatment of characters?
#   TODO: 2020-12-10T23:06:34AEDT option - get files matching mattern?
_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
_parser.add_argument('-v', '--debug', action='store_true', default=False)

#   dir, prefix, postfix -> get files in dir of the form '[prefix][yyyy]-[mm][postfix]
_parser.add_argument('-D', '--dir', type=_DirPath, help="Path to dir containing tasklogs")
_parser.add_argument('--prefix', type=str, default=None, help="Tasklog filename before Y-m")
_parser.add_argument('--postfix', '-P', type=str, default=None, help="Tasklog filename after Y-m")
#_parser.add_argument('--extension', type=str, default="vimgpg", help="Tasklog filename extension")

_subparser_readlabels = _subparser.add_parser('labels')
_subparser_readlabels = _subparser.add_parser('startendtime')
_subparser_readlabels = _subparser.add_parser('quality')


#_parser.add_argument('-i', '--infile', nargs='?', help="Input to search", type=argparse.FileType('r'))
#_parser.add_argument('-d', '--indir', nargs='?', help="Input directory of files", type=str)
#_parser.add_argument('--name', nargs='?', type=str, default="worklog", help="Name of tasklog")
#_parser.add_argument('-G', '--gpgin', action='store_true', help="Decrypt gpg input")
#_parser.add_argument('-R', '--regfile', nargs='?', help="Specify file containing regex match-group(s)", type=argparse.FileType('r'), default=path_regex_str)


readblock = ReadBlock()
input_gpgin = True

def cliscan():
    try:
        with open(path_regex_str, 'r') as f:
            regex_str = f.read()
    except Exception as e:
        _log.error("%s, %s" % (type(e), str(e)))

    regex_search = re.compile(regex_str, re.MULTILINE)
    _args = _parser.parse_args()


    readblock._printdebug = _args.debug
    #_log.debug("args=(%s)" % str(_args))

    tasklogs_list = _GetFilesList_Monthly(_args.dir, _args.prefix, _args.postfix)

    #print(type(_args.subparsers))
    
    #   For each file found
    for loop_tasklog in tasklogs_list:
        #   Decrypt to stream, or open as stream (decrypted streams are stored in memory)
        if (input_gpgin):
            loop_tasklog_stream = readblock.DecryptGPG2Stream(loop_tasklog)
        else:
            loop_tasklog_stream = open(loop_tasklog, "r")

        if (_args.subparsers == 'labels'):
            _results = readblock.ScanStreamRegex(loop_tasklog_stream, regex_search)
            #print(_result)
            #pprint.pprint(_result)
            print("%s" % str(loop_tasklog))
            for loop_result_dict in _results:
                #print(loop_result_dict)
                for k, v in loop_result_dict.items():
                    print("%s: %s" % (str(k), str(v)))

        if (_args.subparsers == 'startendtime'):
            _results = readblock.ScanStreamRegex(loop_tasklog_stream, regex_search)
            _OFS = "\t"
            #print(_result)
            #pprint.pprint(_result)
            for loop_result_dict in _results:
                #print(loop_result_dict)
                #for k, v in loop_result_dict.items():
                #    print("(%s)=(%s)" % (str(k), str(v)))
                try:
                    print("%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone']))
                except Exception as e:
                    pass

        if (_args.subparsers == 'quality'):
            _results = readblock.ScanStreamRegex(loop_tasklog_stream, regex_search)
            _OFS = "\t"
            #print(_result)
            #pprint.pprint(_result)
            for loop_result_dict in _results:
                #print(loop_result_dict)
                #for k, v in loop_result_dict.items():
                #    print("(%s)=(%s)" % (str(k), str(v)))
                try:
                    print("%s\t%s\t%s\t%s" % (loop_result_dict['starttime'], loop_result_dict['timedone'], loop_result_dict['elapsed'], loop_result_dict['quality']))
                except Exception as e:
                    pass


    #if (args.infile):
    #    stream_shuffeled = readblock._TextIOShuffle(args.infile, gpgin)
    #    readblock.ScanStreamRegex(stream_shuffeled, regex_search)
    #    sys.exit(0)

    #if (args.indir):
    #    tasklog_list = readblock.GetAllTasklogsInDir(args.indir, args.name)
    #    for loop_tasklog in tasklog_list:
    #        with open(loop_tasklog, "r") as f:
    #            stream_shuffeled = readblock._TextIOShuffle(f, gpgin)
    #            readblock.ScanStreamRegex(stream_shuffeled, regex_search)

        #_log.debug("tasklog_list=(%s)" % str(tasklog_list))


#   Call main with args
if __name__ == '__main__':
#   {{{
    cliscan()
#   }}}

#   }}}1
