#   VIM SETTINGS: {{{3
#   VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{2
#from reader_tasklogTaskBlocks.__main__ import _log, flag_exit_on_empty_stdin, flag_exit_on_tty_input
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

flag_exit_on_empty_stdin = True
flag_exit_on_tty_input = True


_logging_format="%(funcName)s:%(levelname)s: %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format=_logging_format, datefmt=_logging_datetime)

class ReadBlock(object):

    #   About: Take a filepath as a string, decrypt said file using the system gpg keychain, and return the contents as a string
    def _ReadGPGFile_ToString(self, file_path):
    #   TODO: 2020-12-29T18:24:32AEST get return code from gpg decrypt 
    #   {{{
        func_name = inspect.currentframe().f_code.co_name
        #   gpg deccrypt arguments
        cmd_gpg_decrypt = ["gpg", "-q", "--decrypt", file_path]
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

    #   About: Take gpg encrypted data as a string, convert it to a byte array, use the system gpg keychain to decrypt, and return the result as a string
    def _ReadGPGData_ToString(self, gpg_data):
    #   {{{
        func_name = inspect.currentframe().f_code.co_name
        #   convert gpg_data -> bytearray(cmd_encrypt_input)
        #   {{{
        gpg_data_bytes = bytearray()
        if (type(gpg_data) == str):
            gpg_data_bytes.extend(gpg_data.encode())
        else:
            gpg_data_bytes.extend(gpg_data)
        #   }}}
        #   gpg deccrypt arguments
        cmd_gpg_decrypt = [ "gpg", "-q", "--decrypt" ]
        #   Use Popen, call cmd_gpg_decrypt, using PIPE for stdin/stdout/stderr
        p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE) 
        result_data_decrypt, result_stderr = p.communicate(input=gpg_data_bytes)
        result_str = result_data_decrypt.decode().rstrip()
        result_stderr = result_stderr.decode().rstrip()
        rc = p.returncode
        if (rc != 0):
            raise Exception("gpg decrypt rc=(%s)" % str(rc))
        #   printdebug:
        #   {{{
        _log.debug("result_strerr=(%s)" % str(result_stderr))
        #   }}}
        #   error/warning if empty:
        #   {{{
        result_str_len = len(result_str)
        _log.debug("result_str_len=(%s)" % str(result_str_len))
        if (result_str_len == 0) and (flag_exit_on_empty_gpgin == True):
            raise Exception("gpg decrypt result_str empty")
        elif (result_str_len == 0):
            _log.warning("gpg decrypt result_str empty")
        #   }}}
        return result_str
    #   }}}

    #   About:  If arg_infile represents an ordinary file, we return it. Otherwise, if we have data from stdin, and/or encrypted data, read it into memory, and return a io.StringIO object containing it.
    def DecryptGPG2Stream(self, arg_infile):
    #   {{{
        input_text = "" 
        _log.debug("arg_infile=(%s)" % str(arg_infile))
        input_text = self._ReadGPGFile_ToString(arg_infile)
        return io.StringIO(input_text)
    #   }}}

    #def GetAllTasklogsInDir(self, arg_dir, arg_name_postfix):
    #    _filename = "[0-9][0-9][0-9][0-9]-[0-9][0-9]" + arg_name_postfix 
    #    tasklog_list = glob.glob(os.path.join(arg_dir, _filename))
    #    return tasklog_list

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

    def SearchStreamLineByLine(self, input_stream, regex_search_labels_list):
    #   {{{
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

    def SearchTaskblock(self, arg_taskblock_str, regex_search_labels_list):
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

    def ScanTaskblocksInStream(self, input_stream, regex_search_labels_list, regex_lines_beginStartEnd_list):
    #   {{{
        """Identify blocks of text in file, beginning after regex_lines_beginStartEnd_list[0], which fall between elements [1]/[2] of the same list respectively, for each, call SearchTaskblock, and append results to results_list"""
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

                    _result = self.SearchTaskblock(taskblock_str, regex_search_labels_list)
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

    def ScanGetNonEmptyLineRange(self, input_stream, regex_rangestart, regex_search_labels_list, regex_lines_beginStartEnd_list):
    #   {{{
        """Get all non-empty lines following line containing regex_rangestart, and pass to SearchTaskblock(), and return list of all results"""
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
                    loop_result = self.SearchTaskblock(linerange_str, regex_search_labels_list)
                    results_list.append(loop_result)
                    linerange_str = ""

        _log.debug("len(results_list)=(%s)" % len(results_list))
        return results_list
    #   }}}


#   }}}1

