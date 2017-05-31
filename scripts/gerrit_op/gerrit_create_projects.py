#!/usr/bin/env python
# _*_ coding=utf-8 _*_

from utils import utils
import re
from call_shell import shell

class create_projects:
    def __init__(self):
        self._utils = utils()
        self.all_cfg = self._utils.cfg_parser()
        self.add_cmd()

    def add_cmd(self):
        #ssh -p <29418> <ACCOUNT>@<IP> gerrit create-project
        _cmd_create_project_prefix = 'ssh -p %s %s@%s gerrit create-project' % (self.all_cfg['_gerrit_ssh_port'],
                                                                                self.all_cfg['_gerrit_account'],
                                                                                self.all_cfg['_gerrit_ip'])
        self.all_cfg['TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX'] = _cmd_create_project_prefix

    #父仓库，一般可用来控制权限
    def create_parent_project(self):
        TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX = self.all_cfg['TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX']
        TARGET_PROJECT_PREFIX = self.all_cfg['_query_parentproject']
        # 首先创建project的parent
        parent_project_sufix = '--permissions-only --empty-commit'
        create_projects_parent = [TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX,
                                  TARGET_PROJECT_PREFIX,
                                  parent_project_sufix]
        self.op_one_proj(create_projects_parent)

    #创建manifest中的每个具体的仓库
    def create_given_projects(self, dict_path_name):
        dict_success_created_project, dict_failed_created_project, dict_existed_project = {}, {}, {}
        TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX = self.all_cfg['TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX']
        TARGET_PROJECT_PREFIX = self.all_cfg['_query_parentproject']
        TARGET_GERRIT_REPO_BRANCH = self.all_cfg['_query_branch']
        if len(TARGET_GERRIT_REPO_BRANCH.split()) != 1: 
            self._utils.print_error('Branch nums should be [one], when create branch for projects.')
     
        # 为manifest中的每个仓库都创建project, branch. 并设置parent的权限
        for repo_path in dict_path_name:
            repo_name = dict_path_name[repo_path]
            gerrit_project_name = repo_name
            if not repo_name.startswith(TARGET_PROJECT_PREFIX):
                gerrit_project_name = '%s/%s' % (TARGET_PROJECT_PREFIX, repo_name)
            project_sufix = '-b %s -p %s --empty-commit' % (TARGET_GERRIT_REPO_BRANCH, TARGET_PROJECT_PREFIX)
            gerrit_create_project_cmd = [TARGET_GERRIT_CMD_CREATE_PROJECT_PREFIX,
                                         gerrit_project_name, project_sufix]
            _each_t_or_f, _each_proj_name = self.op_one_proj(gerrit_create_project_cmd, to_exit=False)
            if _each_t_or_f and not _each_proj_name:
                dict_success_created_project[repo_path] = gerrit_project_name
            elif not _each_t_or_f and _each_proj_name:
                dict_existed_project[repo_path] = gerrit_project_name
            elif not _each_t_or_f and not _each_proj_name:
                dict_failed_created_project[repo_path] = gerrit_project_name
     
        return dict_success_created_project, dict_failed_created_project, dict_existed_project

    # 函数参数顺序def f(必须参数,默认参数,*args,**kwargs)：
    # create_proj_cmd 是一个列表类型
    def op_one_proj(self, create_proj_cmd, to_exit=True):
        _cmd = ' '.join(create_proj_cmd)
        _, create_parent_err, create_parent_returncode = shell(_cmd).call_shell()
        # 创建成功
        if create_parent_returncode == 0 and len(create_parent_err) == 0:
            return True, None
        # 创建仓库时，可以是直接创建成功亦或者仓库本身存在，则不需要推出，否则其他错误是退出检查原因
        elif create_parent_returncode != 0 and create_parent_err is not None:
            if re.search('Project already exists', create_parent_err):
                return False, 'Exists'
        # Unknown错误，手动检查
        else:
            self._utils.print_error('Failed! REASON: %s >>> Please manually check...' % (create_parent_err), to_exit)
            return False, None
