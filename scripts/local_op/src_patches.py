#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import os, sys, subprocess, shutil
from utils import utils
#from call_shell import shell
from utils import shell

class src_patches:
    def __init__(self, script_path):
        self._utils = utils(script_path)
        self.all_cfg = self._utils.cfg_parser()
        self.src_path = self.all_cfg['SOURCE_ABS_PATH']
        self.src_branch = self.all_cfg['SOURCE_BRANCH']
        self.src_base_branch = self.all_cfg['SOURCE_BASE_BRANCH']
        self.src_needpatch_repo = self.all_cfg['SOURCE_ISOLATED_REPO']
        self.src_email_filter = self.all_cfg['COMMITTER_EMAIL_LIST']
        self.src_patch_out = self.all_cfg['PATCH_OUT_PATH']

    def get_src_patches(self):
        if os.path.exists(self.src_patch_out): shutil.rmtree(self.src_patch_out)
        #repo_abs_path = ['%s/%s' % (self.src_path, x) for x in self.src_needpatch_repo]
        for _path in self.src_needpatch_repo:
            _abs_path = '%s/%s' % (self.src_path, _path)
            _patch_out = '%s/%s' % (self.src_patch_out, _path)
            #清空patch out目录
            if not os.path.exists(_patch_out): os.makedirs(_patch_out)
            else: shutil.rmtree(_patch_out)

            _tmp_md = self._utils.patch_out_file
            _meta_data_log_file = '%s/%s' % (_patch_out, _tmp_md)
            _meta_data_log_list = []

            print '>>> Gen patches for %s' % _abs_path
            os.chdir(_abs_path)
            if not os.path.exists('.git'):
                self._utils.print_error('错误: %s 不是一个git仓库' % _abs_path)
                return
            self.src_base_branch = self._utils.if_branch_exist(_path, self.src_base_branch)
            self.src_branch = self._utils.if_branch_exist(_path, self.src_branch)

            _get_branch_diff = "git log --no-merges --pretty='%s' --committer='%s' %s..%s | tac > %s" % \
                                  (u'%H', self.src_email_filter, self.src_base_branch, self.src_branch, _tmp_md)
            _branch_diff_result, _, _ = shell(_get_branch_diff).call_shell(False, True)
            with open(_tmp_md) as f:
                _all_sha1 = [x.rstrip('\n') for x in f.readlines()]
                for i in range(len(_all_sha1)-1): # 去掉最后一个sha1，其不需要再生成patch
                   _format_patch_cmd = 'git format-patch -1 --start-number %s %s -o %s' % \
                                          (str(i+1), _all_sha1[i], _patch_out)
                   _patch_out_name, _, _ = shell(_format_patch_cmd).call_shell(True, False)
                   _meta_data = '%s,%s' % (_all_sha1[i], _patch_out_name[len(_patch_out)+1:])
                   _meta_data_log_list.append(_meta_data)

            with open(_meta_data_log_file, 'a+') as meta_f:
                meta_f.writelines(_meta_data_log_list)
