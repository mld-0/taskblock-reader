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

    #   {{{
    #   About: Take a filepath as a string, decrypt said file using the system gpg keychain, and return the contents as a string
    #   Args:
    #       file_path, string containing path to file to be decrypted 
    #   History:
    #   Labeled: (2020-05-14)-(1721-08)
    #   }}}
    def _ReadGPGFile_ToString(self, file_path):
    #   {{{
        func_name = inspect.currentframe().f_code.co_name
        #   gpg deccrypt arguments
        cmd_gpg_decrypt = ["gpg", "-q", "--decrypt", file_path]
        p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        result_data_decrypt, result_stderr = p.communicate()
        result_str = result_data_decrypt.decode()
        result_stderr = result_stderr.decode()
        #   printdebug:
        #   {{{
        if (self._printdebug):
            _log.debug("result_strerr=(%s)" % (str(result_stderr)))
        #   }}}
        #   error/warning if empty:
        #   {{{
        result_str_len = len(result_str)
        if (self._printdebug):
            _log.debug("result_str_len=(%s)" % str(result_str_len))
        if (result_str_len == 0) and (flag_exit_on_empty_gpgin == True):
            _log.error("gpg decrypt result_str empty")
            return None
        elif (result_str_len == 0):
            _log.warning("gpg decrypt result_str empty")
        #   }}}
        return result_str
    #   }}}

    #   {{{
    #   About: Take gpg encrypted data as a string, convert it to a byte array, use the system gpg keychain to decrypt, and return the result as a string
    #   Args:
    #       gpg_data    string/bytearray containing gpg input 
    #   History:
    #   Labeled: (2020-05-14)-(1832-48)
    #   }}}
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
        #   {{{
        cmd_gpg_decrypt = [ "gpg", "-q", "--decrypt" ]
        #   }}}
        #   Use Popen, call cmd_gpg_decrypt, using PIPE for stdin/stdout/stderr
        #   {{{
        p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE) 
        result_data_decrypt, result_stderr = p.communicate(input=gpg_data_bytes)
        result_str = result_data_decrypt.decode()
        result_str = result_str.rstrip()
        result_stderr = result_stderr.decode()
        #   }}}
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
            _log.error("gpg decrypt result_str empty")
            return None
        elif (result_str_len == 0):
            _log.warning("gpg decrypt result_str empty")
        #   }}}
        return result_str
    #   }}}

    #   {{{
    #   About:  If arg_infile represents an ordinary file, we return it. Otherwise, if we have data from stdin, and/or encrypted data, read it into memory, and return a io.StringIO object containing it.
    #   Args:
    #       arg_infile, TextIOWrapper object as created by argparse
    #       input_gpg, if True, attempt to decrypt the input using Util_ReadGPG functions
    #       input_gpg, whether we attempt to decrypt input
    #   History:
    #   Labeled: (2020-05-14)-(1720-40)
    #   }}}
    def DecryptGPG2Stream(self, arg_infile, input_gpg=False):
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

    def ScanStreamRegex(self, input_stream, regex_search):
        matches_count=0
        input_text = ""
        #   Examining file for multi-line regex -> do we need file (as string) in memory?
        for loop_line in input_stream:
            input_text += loop_line
        for loop_match in regex_search.finditer(input_text):
            loop_dict = loop_match.groupdict()
            matches_count += 1
            for k, v in loop_dict.items():
                _log.debug("(%s)=(%s)" % (k, v.strip()))
            print()
        _log.debug("matches_count=(%s)" % str(matches_count))

#   }}}1

