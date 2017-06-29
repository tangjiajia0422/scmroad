#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import os, sys, subprocess, shutil
from utils import utils
from utils import shell
#from call_shell import shell

class auto_clean:
    def __init__(self, script_path):
        self._utils = utils(script_path)
        self.all_cfg = self._utils.cfg_parser()
        self.src_path = self.all_cfg['SOURCE_ABS_PATH']
        self.src_branch = self.all_cfg['SOURCE_BRANCH']
        self.src_base_branch = self.all_cfg['SOURCE_BASE_BRANCH']
        self.src_needpatch_repo = self.all_cfg['SOURCE_ISOLATED_REPO']
        self.src_email_filter = self.all_cfg['COMMITTER_EMAIL_LIST']
        self.src_patch_out = self.all_cfg['PATCH_OUT_PATH']
        self.target_path = self.all_cfg['TARGET_ABS_PATH']
        self.target_backup_branch = self.all_cfg['TARGET_BACKUP_BRANCH']

    def auto_clean(self):
        clean_cmd = 'git clean -dfx; \
                     git reset --hard; \
                     backhead=$(git log -1 --pretty="%s" %s); \
                     git checkout -f "${backhead}"; \
                     sleep 0.1; git branch -D %s' % \
                     (u'%H', self.target_backup_branch, self.target_backup_branch)
        for _path in self.src_needpatch_repo:
            _abs_path = '%s/%s' % (self.target_path, _path)
            if os.path.exists(_abs_path):
                os.chdir(_abs_path)
                shell(clean_cmd).call_shell(False, True)
        try:
            shutil.rmtree(self.src_patch_out)
        except:
            pass
        finally:
            print 'Clean done.'
