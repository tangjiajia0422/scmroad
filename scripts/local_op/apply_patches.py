#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import os, sys, subprocess, shutil
from utils import utils
from utils import shell
#from call_shell import shell

class apply_patches:
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
        self.target_done_patch_log = '.cherrypick_done.log'
        self._target_repo_not_found = []
        self._target_repo_cherrypick_done = []

    def apply_all(self):
        #_to_apply_path = ['%s/%s' % (self.target_path, x) for x in self.src_needpatch_repo]

        #tmp collections
        _done_patches = []

        for _path in self.src_needpatch_repo:
            _abs_path = '%s/%s' % (self.target_path, _path)
            _patch_out_path = '%s/%s' % (self.src_patch_out, _path)
            _patch_out_log = '%s/%s' % (_patch_out_path, self._utils.patch_out_file)
            _patch_done_log = '%s/%s' % (_patch_out_path, self.target_done_patch_log)

            if not os.path.exists(_abs_path):  #target目录中列出的repo找不到，跳过打patch的过程
                self._utils.print_error('%s目录不存在, 跳过...' % _abs_path, False)
                self._target_repo_not_found.append(_path)
                continue
            else: #target目录中也有该repo，则需要patch
                if not os.path.exists('%s/%s' % (_abs_path, '.git')): #有可能结构的变更，虽然目录存在，但不是一个.git仓库
                    self._utils.print_error('%s不是一个git仓库, 跳过...' % _abs_path, False)
                    self._target_repo_not_found.append(_path)
                    continue 
                else: #目录存在，并且是一个.git仓库，执行apply的过程
                    os.chdir(_abs_path)

                    #TODO要判断当前.git目录是否干净
                    _if_git_clean_cmd = 'git diff-index --quiet HEAD --'
                    _, _, _return_code = shell(_if_git_clean_cmd).call_shell(True, False)
                    if _return_code != 0 or os.path.exists('.git/rebase-apply/patch'):  #当前工作目录不干净
                        self._utils.print_error('错误: %s脏工作区，请检查，可以执行命令: $git add; git commit' % (_abs_path))

                    if os.path.exists(_patch_done_log):
                        with open(_patch_done_log) as done_f:
                            _done_patches = [x.rstrip('\n') for x in done_f.readlines()]
                    else:
                        #在第一次进入到目录时，创建一个本地分支，为了标记当前所在的HEAD，并为clean的操作提供了branch
                        if not self._utils.if_branch_exist(_abs_path, self.target_backup_branch, False):
                            self._utils.print_error('正在为%s创建标记分支: %s...' % (_path, self.target_backup_branch),False, False)
                            _backup_branch_cmd = 'git branch %s HEAD' % self.target_backup_branch
                            _, _, _return_code = shell(_backup_branch_cmd).call_shell(False, False)
                            if _return_code != 0: self._utils.print_error('创建纯净标记分支%s失败，可忽略' % self.target_backup_branch, False, False)

                    with open(_patch_out_log) as log_f:
                        _all_patches = [x.rstrip('\n') for x in log_f.readlines()]
                        #如过打过patch的列表比所有patch的列表要小，那么表示之前有错误
                        #既然出现过冲突，冲突也会在_patch_done_log文件中被标注为FAIL，但是下标不会变
                        #假设是第一个patch就有冲突，那么_patch_done_log第一行就是FAIL，那么第二次执行要从第二个(下标为1)
                        #假设第一个成功，第二个失败，那么再次执行就是从第三个开始(下标为2),和len(_done_patches)相等
                        if len(_done_patches) < len(_all_patches):
                            _all_patches = _all_patches[len(_done_patches):]

                        if len(_all_patches) == 0: #表示都已经cherry-pick过了，进入到下一个repo
                            self._target_repo_cherrypick_done.append(_path)
                            continue
                        else:  #从上次失败的下一个开始再继续cherry-pick
                            for _line in _all_patches:
                                _sha1, _patch_name = _line.split(',')
                                _patch_path = '%s/%s' % (_patch_out_path, _patch_name)
                                _apply_cmd = 'git am --reject %s' % (_patch_path)
                                _apply_patch, _err_msg, _return_code = shell(_apply_cmd).call_shell(True, False)
                                if _return_code == 0: # apply 成功
                                    with open(_patch_done_log, 'a+') as done_f:
                                        done_f.write('SUCCESS,%s%s' % (_line, u'\n'))
                                    
                                else: #出错了，需要退出整个方法，下次继续执行
                                    with open(_patch_done_log, 'a+') as done_f:
                                        done_f.write('FAIL,%s%s' % (_line, u'\n'))
                                    self._utils.print_error('''
错误: 仓库%s出现冲突:%s, 
（如果你需要这个patch，那么先解决冲突，然后运行 "git am -A; git am --continue"）
（如果你暂时不想解决冲突，请使用 "git am --skip" 跳过此补丁）
（如果你不需要此patch，请使用 "git am --abort" 恢复原有分支）''' % (_abs_path, _line))

        #输出打patch的结果
        self.patching_result()

    def patching_result(self):
        _result_dict = {'REPO_NOT_FOUND': self._target_repo_not_found, 'REPO_PATCHING_DONE': self._target_repo_cherrypick_done}
        self._utils.print_defined_env(_result_dict)
