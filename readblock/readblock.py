#   VIM SETTINGS: {{{3
#   VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
import inspect
import argparse
import sys
import gnupg
import subprocess
import shutil
import io
import os
import argcomplete
from subprocess import Popen, PIPE, STDOUT
import inspect
from pathlib import Path
import re
import pprint
import logging
import inspect
import os
import time
import glob
import importlib
import importlib.resources
import pprint
import glob
#   }}}1
#   {{{2

flag_exit_on_empty_stdin = True
flag_exit_on_tty_input = True

_logging_format="%(funcName)s:%(levelname)s: %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format=_logging_format, datefmt=_logging_datetime)

class ReadBlock(object):
    input_gpgin = True

    def SearchTasklogs_DefaultSearchLabels(self, arg_tasklog_files_list):
    #   {{{
        regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = self._Read_Resources()
        #tasklog_files_list = self._GetFilesList_Monthly(arg_dir, arg_prefix, arg_postfix)
        results_list = []
        for loop_tasklog in arg_tasklog_files_list:
            if (self.input_gpgin):
                loop_tasklog_stream = self._DecryptGPG2Stream(loop_tasklog)
            else:
                loop_tasklog_stream = open(loop_tasklog, "r")
            _results = self._ScanTaskblocksInStream(loop_tasklog_stream, regex_search_labels_list, regex_lines_beginStartEnd_list)
            results_list.append(_results)
            loop_tasklog_stream.close()
        return results_list
    #   }}}

    def SearchTasklogs_grabitems(self, arg_tasklog_files_list, arg_label=None):
    #   {{{
        regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = self._Read_Resources()
        #tasklog_files_list = self._GetFilesList_Monthly(arg_dir, arg_prefix, arg_postfix)
        results_list = []
        for loop_tasklog in arg_tasklog_files_list:
            if (self.input_gpgin):
                loop_tasklog_stream = self._DecryptGPG2Stream(loop_tasklog)
            else:
                loop_tasklog_stream = open(loop_tasklog, "r")
            #_log.debug("_grab_labels=(%s)" % str(_grab_labels))
            _results = None
            if (arg_label is None):
                _results = self._SearchStreamLineByLine(loop_tasklog_stream, _grab_labels_default)
                results_list.append(_results)
            else:
                _grab_labels = []
                _log.debug("arg_label=(%s)" % str(arg_label))
                for loop_label in arg_label:
                    loop_grablabel = self._CombineGrabLabelRegex(loop_label)
                    _grab_labels.append(loop_grablabel)
                _log.debug("_grab_labels=(%s)" % str(_grab_labels))
                _results = self._SearchStreamLineByLine(loop_tasklog_stream, _grab_labels)
                results_list.append(_results)
            loop_tasklog_stream.close()
        return results_list
    #   }}}

    def SearchTasklogs_todaytasks(self, arg_tasklog_files_list):
    #   {{{
        regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default = self._Read_Resources()
        #tasklog_files_list = self._GetFilesList_Monthly(arg_dir, arg_prefix, arg_postfix)
        results_list = []
        filenames_list = []
        for loop_tasklog in arg_tasklog_files_list:
            if (self.input_gpgin):
                loop_tasklog_stream = self._DecryptGPG2Stream(loop_tasklog)
            else:
                loop_tasklog_stream = open(loop_tasklog, "r")
            _regex_startday = r"^======== StartDay:"
            _regex_todaytasks = [ r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})", r"(?P<todaytasks>Today-Tasks:\s*\n(.*\n)+)" ]
            _results = self._ScanGetNonEmptyLineRangeAfterMatches(loop_tasklog_stream, _regex_startday, _regex_todaytasks, regex_lines_beginStartEnd_list)
            results_list.append(_results)
            loop_tasklog_stream.close()
        return results_list
    #   }}}

    def _DecryptGPG2Stream(self, arg_infile):
    #   {{{
        """Take a filepath as a string, decrypt with _ReadGPGFile_ToString(), and return resulting string as StringIO"""
        input_text = "" 
        _log.debug("arg_infile=(%s)" % str(arg_infile))
        input_text = self._ReadGPGFile_ToString(arg_infile)
        return io.StringIO(input_text)
    #   }}}

    def _ReadGPGFile_ToString(self, arg_filestream):
    #   {{{
        """Take a filepath as a string, decrypt said file using the system gpg keychain, and return the contents as a string"""
        func_name = inspect.currentframe().f_code.co_name
        #   gpg deccrypt arguments
        file_path = None
        if hasattr(arg_filestream, 'name'):
            file_path = arg_filestream.name
        else:
            file_path = arg_filestream
        cmd_gpg_decrypt = ["gpg", "-q", "--decrypt", file_path]
        #cmd_gpg_decrypt = ["gpg", "-q", "--decrypt"]
        #p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=arg_filestream, stderr=PIPE)
        p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        result_data_decrypt, result_stderr = p.communicate()
        result_str = result_data_decrypt.decode().rstrip()
        result_stderr = result_stderr.decode().rstrip()
        rc = p.returncode
        if (rc != 0):
            raise Exception("gpg decrypt rc=(%s)" % str(rc))
        if (len(result_stderr) > 0):
            _log.warning("result_strerr=(%s)" % (str(result_stderr)))
        #   error/warning if empty:
        #   {{{
        result_str_len = len(result_str)
        _log.debug("len(result_str)=(%s)" % str(result_str_len))
        _log.debug("lines(result_str)=(%s)" % str(len(result_str.split("\n"))))
        if (result_str_len == 0) and (flag_exit_on_empty_gpgin == True):
            raise Exception("gpg decrypt result_str empty")
        elif (result_str_len == 0):
            _log.warning("gpg decrypt result_str empty")
        #   }}}
        return result_str
    #   }}}

    #def SearchStreamMultiLine(self, input_stream, regex_search_labels_list):
    ##   {{{
    #    results_list = []
    #    results_dict = dict()
    #    search_text = input_stream.read()
    #    for loop_regex in regex_search_labels_list:
    #        _result = re.search(loop_regex, search_text, re.MULTILINE)
    #        try:
    #            loop_dict = _result.groupdict()
    #            for k, v in loop_dict.items():
    #                #_log.debug("k=(%s), v=(%s)" % (str(k), str(v)))
    #                results_dict[k] = v
    #            #_log.debug("loop_dict=(%s)" % str(loop_dict))
    #        except Exception as e:
    #            pass
    #    #_log.debug("len(results_dict=(%s)" % len(results_dict))
    #    if (len(results_dict) > 0):
    #        results_list.append(results_dict)
    #    return results_list
    ##   }}}

    def _SearchStreamLineByLine(self, input_stream, regex_search_labels_list):
    #   {{{
        """Return dictionary of matches for named capture groups from regex list in stream"""
        results_list = []
        for loop_line in input_stream:
            results_dict = dict()
            for loop_regex in regex_search_labels_list:
                _result = re.search(loop_regex, loop_line)
                try:
                    loop_dict = _result.groupdict()
                    for k, v in loop_dict.items():
                        #_log.debug("k=(%s), v=(%s)" % (str(k), str(v)))
                        results_dict[k] = v
                    #_log.debug("loop_dict=(%s)" % str(loop_dict))
                except Exception as e:
                    pass
            #_log.debug("len(results_dict=(%s)" % len(results_dict))
            if (len(results_dict) > 0):
                results_list.append(results_dict)
        return results_list
    #   }}}

    def _SearchTaskblock(self, arg_taskblock_str, regex_search_labels_list):
    #   {{{
        """Given a taskblock as string, and list of regex-as-strings, return dict of search results for results from named capture groups"""
        results_dict = dict()
        for loop_regex in regex_search_labels_list:
            _result = re.search(loop_regex, arg_taskblock_str, re.MULTILINE)
            #_log.debug("_result=(%s)" % str(_result))
            try:
                loop_dict = _result.groupdict()
                for k, v in loop_dict.items():
                    #_log.debug("k=(%s), v=(%s)" % (str(k), str(v)))
                    results_dict[k] = v
                #_log.debug("loop_dict=(%s)" % str(loop_dict))
            except Exception as e:
                pass
        #_log.debug("len(results_dict=(%s)" % len(results_dict))
        if (len(results_dict) > 0):
            return results_dict
        else:
            return None
    #   }}}

    def _ScanTaskblocksInStream(self, input_stream, regex_search_labels_list, regex_lines_beginStartEnd_list):
    #   {{{
        """Identify taskblocks - blocks of text in file, beginning after regex_lines_beginStartEnd_list[0], which fall between elements [1]/[2] of the same list respectively, for each, call _SearchTaskblock, and append results to results_list"""
        results_list = []
        #taskblock_str_list = []
        taskblock_str = ""
        flag_found_begin = False

        regex_line_begin = regex_lines_beginStartEnd_list[0]
        regex_line_start = regex_lines_beginStartEnd_list[1]
        regex_line_end = regex_lines_beginStartEnd_list[2]

        for loop_line in input_stream:
            if not (flag_found_begin) and re.match(regex_line_begin, loop_line):
                flag_found_begin = True

            if (flag_found_begin):
                if re.match(regex_line_end, loop_line):
                    taskblock_str += loop_line

                    _result = self._SearchTaskblock(taskblock_str, regex_search_labels_list)
                    if (_result is not None):
                        results_list.append(_result)
                    #taskblock_str_list.append(taskblock_str)
                    taskblock_str = ""
                elif re.match(regex_line_start, loop_line):
                    if (len(taskblock_str) > 0):
                        #taskblock_str_list.append(taskblock_str)
                        taskblock_str = ""
                    taskblock_str += loop_line
                elif (len(taskblock_str) > 0):
                    taskblock_str += loop_line

        _log.debug("len(results_list)=(%s)" % len(results_list))
        return results_list
    #   }}}

    def _ScanGetNonEmptyLineRangeAfterMatches(self, input_stream, regex_rangestart, regex_search_labels_list, regex_lines_beginStartEnd_list):
    #   {{{
        """Get all non-empty lines following line containing regex_rangestart, and pass to _SearchTaskblock(), and return list of all results"""
        results_list = []
        linerange_str = ""
        flag_found_begin = False

        regex_line_begin = regex_lines_beginStartEnd_list[0]
        regex_line_start = regex_lines_beginStartEnd_list[1]
        regex_line_end = regex_lines_beginStartEnd_list[2]

        for loop_line in input_stream:
            if not (flag_found_begin) and re.match(regex_line_begin, loop_line):
                flag_found_begin = True

            if (flag_found_begin):
                if re.match(regex_rangestart, loop_line):
                    loop_line = loop_line.replace('{{'+'{', '')
                    linerange_str += loop_line
                elif len(linerange_str) > 0 and len(loop_line.strip()) > 0:
                    linerange_str += loop_line
                elif len(linerange_str) > 0:
                    #results_list.append(linerange_str)
                    linerange_str = linerange_str.strip()
                    loop_result = self._SearchTaskblock(linerange_str, regex_search_labels_list)
                    results_list.append(loop_result)
                    linerange_str = ""

        _log.debug("len(results_list)=(%s)" % len(results_list))
        return results_list
    #   }}}

    def _CombineGrabLabelRegex(self, arg_label):
    #   {{{
        """Create 'grabblock' search regex from label, label may be preceded only by non-word chars excluding newline, and followed by ':', capture group name is the label with s/\W/_/g"""
        _grab_label_prefix = r"^[^\w\n]*"
        _grab_label_postfix = r": "
        _capturegroup_Label = re.sub(r"\W", "_", arg_label)
        regex_result = _grab_label_prefix + arg_label + _grab_label_postfix + r"(?P<" + _capturegroup_Label + r">.*)$"
        _log.debug("regex_result=(%s)" % str(regex_result))
        return regex_result
    #   }}}

    def _Read_Resources(self):
    #   {{{
        """Read resource files in package, and return lists created from each such file. First is labels of a taskblock, second is tasklog current marker and first/last item of each taskblock, third is the 'grab' labels"""
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
                    loop_grablabel = self._CombineGrabLabelRegex(loop_line.strip())
                    _grab_labels_default.append(loop_grablabel)
        except Exception as e:
            _log.error("%s, %s" % (type(e), str(e)))
            raise Exception("Failed to read path_grab_labels=(%s)" % str(path_grab_labels))
        #   }}}
        return [ regex_search_labels_list, regex_lines_beginStartEnd_list, _grab_labels_default ] 
    #   }}}

    def _GetFilesList_Monthly(self, arg_dir, arg_prefix, arg_postfix):
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
        results_list.sort(reverse=True)
        _log.debug("results_list:\n%s" % pprint.pformat(results_list))
        return results_list
    #   }}}

#   }}}1

