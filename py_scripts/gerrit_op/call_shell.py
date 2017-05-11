#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import sys, subprocess

class shell:
    def __init__(self, _cmd):
        if _cmd:
            self._cmd = _cmd
        else:
            print 'You want to exec shell, but cmd is None...'
            sys.exit(-1)

    def call_shell(self, exit=True):
        print 'Executing shell cmd >>> ', self._cmd
        pipe = subprocess.Popen("%s" % self._cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errmsg = pipe.communicate()
        popen_returncode = pipe.returncode
        if not errmsg and len(errmsg) != 0 and popen_returncode != 0:
            if exit:
                print errmsg
                sys.exit(-1)
            else:
                print 'Ignore the shell std error：%s' % (errmsg[0:200]) #截取err的前200个字符
        return output, errmsg, popen_returncode
