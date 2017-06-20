#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import os, sys
from utils import utils
from utils import shell
#from call_shell import shell

class version_check:
    def __init__(self, script_path):
        self._utils = utils(script_path)

    def check_all_versions(self):
        self.python_version()
        self.git_version()

    def python_version(self):
        cur_version = sys.version_info
        if cur_version < (2, 6) or cur_version > (3, 0):
            self._utils.print_error('Python version error: only 2.7.x is supported..')

    def git_version(self):
        git_version_cmd = 'git --version'
        _out,_ , _return_code = shell(git_version_cmd).call_shell(False, False)
        if _return_code != 0:
            self._utils.print_error('Make sure you have installed git first...')
