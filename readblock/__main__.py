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
from .readblock import ReadBlock
#   {{{2

#   Usage:
#>%     python run-taskblock-reader.py --infile /Users/mldavis/Dropbox/_TaskLogs/_worklog/2020-12.worklog.vimgpg
#   Only works with tasklogs new enough to use the format of that given in the file,
#   crashes on older files (those with no matches at all?)


#path_home = os.path.expanduser("~")
#path_templates_dir = os.path.join(path_home, "_templates")
#path_regex_str = os.path.join(path_templates_dir, "tasklog-taskblock-asregex.txt")

path_regex_str= None
with importlib.resources.path("readblock", "regexfile-taskblock.txt") as p:
    path_regex_str = str(p)


_logging_format="%(funcName)s:%(levelname)s: %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

#   Include default values in help
parser = argparse.ArgumentParser(description="Read line(s) in file beginning with specified labels in groups", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#   TODO: 2020-11-08T12:21:37AEDT Read regex from file - treatment of characters?

#   TODO: 2020-12-10T23:06:34AEDT option - get files matching mattern?
parser.add_argument('--version', action='version', version="0.0.1")
parser.add_argument('-i', '--infile', nargs='?', help="Input to search", type=argparse.FileType('r'))

#parser.add_argument('-d', '--indir', nargs='?', help="Input directory of files", type=str)
#parser.add_argument('--name', nargs='?', type=str, default="worklog", help="Name of tasklog")
#parser.add_argument('-G', '--gpgin', action='store_true', help="Decrypt gpg input")
#parser.add_argument('-R', '--regfile', nargs='?', help="Specify file containing regex match-group(s)", type=argparse.FileType('r'), default=path_regex_str)

readblock = ReadBlock()
gpgin = True

def cliscan():
    try:
        with open(path_regex_str, 'r') as f:
            regex_str = f.read()
    except Exception as e:
        _log.error("%s, %s" % (type(e), str(e)))
    regex_search = re.compile(regex_str, re.MULTILINE)
    args = parser.parse_args()
    _log.debug("args=(%s)" % str(args))
    
    if (args.infile):
        stream_shuffeled = readblock._TextIOShuffle(args.infile, gpgin)
        readblock.ScanStreamRegex(stream_shuffeled, regex_search)

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
