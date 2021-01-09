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
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class ReadBlock(object):
    _printdebug = False

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
        if (self._printdebug):
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
        if (self._printdebug == 1):
            _log.debug("result_strerr=(%s)" % str(result_stderr))
            _log.debug("result_strerr=(%s)" % str(result_str))
        #   }}}
        #   error/warning if empty:
        #   {{{
        result_str_len = len(result_str)
        if (self._printdebug == 1):
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
        if (self._printdebug):
            _log.debug("arg_infile=(%s)" % str(arg_infile))
        input_text = self._ReadGPGFile_ToString(arg_infile)
        return io.StringIO(input_text)
        #   }}}
#   }}}

    def GetAllTasklogsInDir(self, arg_dir, arg_name):
        tasklog_list = glob.glob(arg_dir  + "[0-9][0-9][0-9][0-9]-[0-9][0-9]." + arg_name + ".vimgpg" )
        return tasklog_list

    def ReadSearchStr(self, arg_search_str, regex_search):
        #results_list = []
        results_dict = dict()

        search_regex = [ r"^[ \t]*ITEM:[ \t]*(?P<item>.+?)$", r"^[ \t]*Start-Time:[ \t]+(?P<starttime>.+?)$", r"^[ \t]*TimeQuality:[ \t]*(?P<quality>.+?)$", r"^[ \t]*Time-Done:[ \t]*(?P<timedone>.+?)$", r"^[ \t]*Block-Elapsed:[ \t]*(?P<elapsed>.+?)$" ]

        result_dict_list = []
        for loop_regex in search_regex:
            _result = re.search(loop_regex, arg_search_str, re.MULTILINE)
            #_log.debug("_result=(%s)" % str(_result))

            _result_dict = None
            try:
                _result_dict = _result.groupdict()
                for k, v in _result_dict.items():
                    _log.debug("k=(%s), v=(%s)" % (str(k), str(v)))
                    results_dict[k] = v
                #_log.debug("_result_dict=(%s)" % str(_result_dict))
            except Exception as e:
                pass

            #results_list.append(_result_dict)


        #_log.debug("arg_search_str=(%s)" % str(arg_search_str))
        #results_list = regex_search.findall(arg_search_str)

        #_log.debug("len(results_list)=(%i)" % len(results_list))

        #return results_list
        #return None
        return results_dict

    def ScanStreamRegex(self, input_stream, regex_search):
        matches_count=0
        input_text = ""
        #   Examining file for multi-line regex -> do we need file (as string) in memory?

        results_list = []
        search_str_list = []
        search_str = ""
        flag_found_begin = False
        regex_line_begin = r"^[ \t]*#------CurrentPrevious-FoldMarker-CURRENT--{{{1"
        regex_line_start = r"^[ \t]*ITEM:"
        regex_line_end = r"^[ \t]*Block-Elapsed:"

        for loop_line in input_stream:
            if re.match(regex_line_begin, loop_line):
                flag_found_begin = True

            if (flag_found_begin):
                if re.match(regex_line_end, loop_line):
                    search_str += loop_line

                    _result = self.ReadSearchStr(search_str, regex_search)
                    results_list.append(_result)
                    search_str_list.append(search_str)

                    search_str = ""
                elif re.match(regex_line_start, loop_line):
                    if (len(search_str) > 0):
                        search_str_list.append(search_str)
                        search_str = ""
                    search_str += loop_line
                elif (len(search_str) > 0):
                    search_str += loop_line

        #_log.debug("len(search_str_list)=(%s)" % len(search_str_list))
        _log.debug("len(results_list)=(%s)" % len(results_list))
        #_log.debug("search_str_list=(%s)" % str(search_str_list))
        #_log.debug("results_list=(%s)" % str(results_list))

        return results_list

        #_log.debug("search_str_list=(%s)" % search_str_list)
        #results_list = regex_search.findall(search_str, re.DOTALL)
        #_log.debug("len(results_list)=(%s)" % str(len(results_list)))
        #for loop_match in results_list:
        #    #_log.debug("loop_match=(%s)" % str(loop_match))
        #    #loop_dict = loop_match.groupdict()
        #    matches_count += 1
        #    #for k, v in loop_dict.items():
        #    #    _log.debug("(%s)=(%s)" % (k, v.strip()))
        #_log.debug("matches_count=(%s)" % str(matches_count))

#   }}}1

