#!/usr/bin/env python
# _*_ coding=utf-8 _*_

from abc import ABCMeta, abstractmethod
import ConfigParser, os
from utils import utils

class gerrit_query:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.all_cfg = utils().cfg_parser()

    @abstractmethod
    def _query(self): pass

    @abstractmethod
    def gen_query_cmd(): pass

    '''
    一般来说，一个项目的分支不超过5个，而repo可能会有几十~几百个
    因此拆分branch
    '''
    def split_branches_and_projects(self):
        _query_branches, _query_projects = self.all_cfg['_query_branch'], self.all_cfg['_query_projects']
        result = {}
        if _query_branches and _query_projects:
            branches = _query_branches.split()
            projects = _query_projects.split()
            for _branch in branches:
                result[_branch] = projects
        elif _query_branches and not _query_projects:
            result['BRANCHES_MARK'] = _query_branches.split()
        elif not _query_branches and _query_projects:
            result['PROJECTS_MARK'] = _query_projects.split()
        else:
            return None
        return result

    def __str__(self):
        max_key_len = max([len(x) for x in self.all_cfg])
        return os.linesep.join(["{f_key:>{key_len}} : {f_value:<}".format(f_key=_key, key_len=max_key_len, f_value=self.all_cfg[_key]) for _key in self.all_cfg])
