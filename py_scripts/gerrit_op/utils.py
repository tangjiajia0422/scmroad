#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import time, datetime, os
import ConfigParser

class utils:
    def __init__(self): pass

    def cfg_parser(self):
        cfg_parser = ConfigParser.ConfigParser()
        cfg_parser.read("gerrit_query.cfg")
        all_cfg = {}
        all_cfg['_gerrit_protocol'] = cfg_parser.get("gerrit", "GERRIT_PROTOCOL")
        all_cfg['_gerrit_ip'] = cfg_parser.get("gerrit", "GERRIT_IP")
        all_cfg['_gerrit_sufix'] = cfg_parser.get("gerrit", "GERRIT_SUFIX")
        all_cfg['_gerrit_ssh_port'] = cfg_parser.get("gerrit", "GERRIT_SSH_PORT")
        all_cfg['_gerrit_account'] = cfg_parser.get("gerrit", "GERRIT_ACCOUNT")
        all_cfg['_gerrit_http_pwd'] = cfg_parser.get("gerrit", "GERRIT_HTTP_PWD")

        all_cfg['_query_branch'] = cfg_parser.get("query", "BRANCHES")
        all_cfg['_query_status'] = cfg_parser.get("query", "STATUS")
        all_cfg['_query_parentproject'] = cfg_parser.get("query", "PARENTPROJECT")
        all_cfg['_query_projects'] = cfg_parser.get("query", "PROJECTS")
        if all_cfg['_query_parentproject']:
            all_cfg['_query_projects'] = ''
        if all_cfg['_query_projects']:
            all_cfg['_query_parentproject'] = ''
        all_cfg['_query_frequency'] = cfg_parser.get("query", "HTTP_QUERY_FREQUENCY")
        all_cfg['_out_items'] = cfg_parser.get("query", "OUT_ITEMS")
        return all_cfg

    def readable_timestamp(self, timestamp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(timestamp)))

    def readable_today(self):
        return datetime.date.today()

    def get_csv_head(self):
        self_defined = self.cfg_parser()['_out_items'].lower().split()
        self_defined.append('parent')
        return self_defined

    def items_result(self, _json_dict):
        _out_items = self.get_csv_head()
        _item_result = []
        if not _json_dict:
            return _item_result

        if 'gerritid' in _out_items: _item_result.insert(_out_items.index('gerritid'), _json_dict['url'])
        if 'branch' in _out_items: _item_result.insert(_out_items.index('branch'), _json_dict['branch'])
        if 'subject' in _out_items: _item_result.insert(_out_items.index('subject'), _json_dict['subject'])
        if 'project' in _out_items: _item_result.insert(_out_items.index('project'), _json_dict['project'])
        if 'owner' in _out_items: _item_result.insert(_out_items.index('owner'), _json_dict['owner']['email'])
        if 'author' in _out_items: _item_result.insert(_out_items.index('author'), _json_dict['currentPatchSet']['author']['email'])
        if 'commitid' in _out_items: _item_result.insert(_out_items.index('commitid'), _json_dict['currentPatchSet']['revision'])
        if 'comments' in _out_items: _item_result.insert(_out_items.index('comments'), _json_dict['commitMessage'].replace(',', '_').replace('\n', ' '))
        if 'files' in _out_items: _item_result.insert(_out_items.index('files'), os.linesep.join([_dict['file'] for _dict in _json_dict['currentPatchSet']['files']]))
        if 'time' in _out_items: _item_result.insert(_out_items.index('time'), self.readable_timestamp(_json_dict['lastUpdated']))
        if 'totalline' in _out_items: _item_result.insert(_out_items.index('totalline'), int(_json_dict['currentPatchSet']['sizeInsertions']) + int(_json_dict['currentPatchSet']['sizeDeletions']))
        if 'allreviewers' in _out_items: _item_result.insert(_out_items.index('allreviewers'), os.linesep.join([_dict['email'] for _dict in _json_dict['allReviewers']]))

        _patchset_parents = _json_dict['currentPatchSet']['parents']
        _item_result.append('merge-commit') if len(_patchset_parents) > 1 else _item_result.append(_patchset_parents[0])
        
        return _item_result
