#!/usr/bin/env python
# _*_ coding=utf-8 _*_

from utils import utils
from call_shell import shell

class create_branch:
    def __init__(self):
        self._utils = utils()
        self.all_cfg = self._utils.cfg_parser()
        self.add_cmd()

    def add_cmd(self):
        #ssh -p <29418> <ACCOUNT>@<IP> gerrit create-project
        _cmd_create_branch_prefix = 'ssh -p %s %s@%s gerrit create-branch' % (self.all_cfg['_gerrit_ssh_port'],
                                                                                self.all_cfg['_gerrit_account'],
                                                                                self.all_cfg['_gerrit_ip'])
        self.all_cfg['TARGET_GERRIT_CMD_CREATE_BRANCH_PREFIX'] = _cmd_create_branch_prefix

    #创建manifest中的每个具体的仓库的分支
    def create_given_branch(self, dict_path_name):
        dict_success_created_branch, dict_failed_created_branch = {}, {}
        TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX = self.all_cfg['TARGET_GERRIT_CMD_CREATE_BRANCH_PREFIX']
        TARGET_PROJECT_PREFIX = self.all_cfg['_query_parentproject']
        TARGET_GERRIT_REPO_BRANCH = self.all_cfg['_query_branch']
        NEW_BRANCH = self.all_cfg['_new_branch']
        if len(TARGET_GERRIT_REPO_BRANCH.split()) != 1 or len(NEW_BRANCH.split()) != 1: 
            self._utils.print_error('Branch nums should be [one], when create branch for projects.')
     
        # 为manifest中的每个仓库都创建branch. 并设置parent的权限
        for repo_path in dict_path_name:
            repo_name = dict_path_name[repo_path]
            gerrit_project_name = repo_name
            if not repo_name.startswith(TARGET_PROJECT_PREFIX):
                gerrit_project_name = '%s/%s' % (TARGET_PROJECT_PREFIX, repo_name)
            branch_sufix = '%s %s' % (NEW_BRANCH, TARGET_GERRIT_REPO_BRANCH)
            gerrit_create_project_cmd = [TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX,
                                         gerrit_project_name, branch_sufix]
            _each_t_or_f, _each_proj_name = self.op_one_proj(gerrit_create_project_cmd, to_exit=False)
            if _each_t_or_f and not _each_proj_name:
                dict_success_created_branch[repo_path] = gerrit_project_name
            elif not _each_t_or_f and not _each_proj_name:
                dict_failed_created_branch[repo_path] = gerrit_project_name
     
        return dict_success_created_branch, dict_failed_created_branch

    # 函数参数顺序def f(必须参数,默认参数,*args,**kwargs)：
    # create_proj_cmd 是一个列表类型
    def op_one_proj(self, create_proj_cmd, to_exit=True):
        _cmd = ' '.join(create_proj_cmd)
        print _cmd
        _, create_parent_err, create_parent_returncode = shell(_cmd).call_shell()
        # 创建成功
        if create_parent_returncode == 0 and len(create_parent_err) == 0:
            return True, None
        # 错误，手动检查
        else:
            self._utils.print_error('Failed! REASON: %s >>> Please manually check...' % (create_parent_err), to_exit)
            return False, None
