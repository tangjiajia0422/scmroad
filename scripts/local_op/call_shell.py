#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import sys, subprocess
from utils import utils

class shell:
    def __init__(self, _cmd):
        self.utils = utils('')
        if _cmd:
            self._cmd = _cmd
        else:
            self.utils.print_error('命令为空，没有命令可以执行...')

    def call_shell(self, willprint=True, exit=True):
        if willprint:
           print 'Executing shell cmd >>> ', self._cmd
        pipe = subprocess.Popen("%s" % self._cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errmsg = pipe.communicate()
        popen_returncode = pipe.returncode
        if not errmsg and len(errmsg) != 0 and popen_returncode != 0:
            if exit:
                self.utils.print_error(errmsg[0:200])
            #else:
            #    self.utils.print_error('跳过错误: %s' % errmsg[0:200], False) #截取err的前200个字符
        return output, errmsg, popen_returncode
