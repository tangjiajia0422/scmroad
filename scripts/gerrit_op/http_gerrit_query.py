#!/usr/bin/env python
# _*_ coding=utf-8 _*_

from gerrit_query import gerrit_query
from call_shell import shell
import json

class http_gerrit_query(gerrit_query):

    def __init__(self, query_method='http'):
        super(http_gerrit_query, self).__init__()
        self.all_cfg['_query_method'] = query_method

    '''
    Gerrit document:
      Authentication
      By default all REST endpoints assume anonymous access and filter results to correspond to what anonymous users can read (which may be nothing at all).
      Users (and programs) may authenticate by prefixing the endpoint URL with /a/. For example to authenticate to /projects/, request the URL /a/projects/.
      By default Gerrit uses HTTP digest authentication with the HTTP password from the user’s account settings page. HTTP basic authentication is used if auth.gitBasicAuth is set to true in the Gerrit configuration.
    命令示例:
      (1):curl --digest -u 'HTTP_ACCOUNT:HTTP_PWD' -X GET -s "http://192.168.67.126:8080/a/changes/?q=-age:5min+project:tools/cmtools+branch:master+status:merged"
      (2):curl --digest -u 'HTTP_ACCOUNT:HTTP_PWD' -X GET -s "http://192.168.67.126:8080/a/changes/?q=age:5min+project:tools/cmtools+branch:master+status:merged"
      (1)和(2)的区别在与"q=-age:5min"，"q=age:5min"，前者是查询的5分钟内的，后者查询的是已存在了5分钟的，也就是5分钟之前的！
    '''
    def gen_query_cmd(self):
        branch_project = self.split_branches_and_projects() #字典类型
        all_filter, _query_filter = [], []
        _curl_prefix = "curl -k --digest -u '%s:%s' -X GET " % (self.all_cfg['_gerrit_account'], self.all_cfg['_gerrit_http_pwd'])
        if branch_project: #有branch或者project已或者两者都有
            _key = branch_project.keys()[0]
            if _key == 'BRANCHES_MARK':
                for _branch in branch_project.values()[0]:
                    _query_filter.append('branch:%s' % _branch)
                    all_filter.append(_query_filter)
                    _query_filter = []
            elif _key == 'PROJECTS_MARK':
                for _project in branch_project.values()[0]:
                    _query_filter.append('project:%s' % _project)
                    all_filter.append(_query_filter)
                    _query_filter = []
            else:
                for _branch in branch_project:
                    for _project in branch_project[_branch]:
                        _query_filter.append('branch:%s' % _branch)
                        _query_filter.append('project:%s' % _project)
                        all_filter.append(_query_filter)
                        _query_filter = []
        
        all_filter = all_filter if all_filter else [[]]
        if self.all_cfg['_query_frequency']:
            [freq.insert(0,'-age:%s' % self.all_cfg['_query_frequency']) for freq in all_filter]
        if self.all_cfg['_query_parentproject']:
            [parent.append('parentproject:%s' % self.all_cfg['_query_parentproject']) for parent in all_filter]
        if self.all_cfg['_query_status']:
            [status.append('status:%s' % self.all_cfg['_query_status']) for status in all_filter]
        filter_condition = ['+'.join(_filter) for _filter in all_filter]
        query_filter = "%s -s %s://%s%s/a/changes/?q=" % (_curl_prefix,
                                                               self.all_cfg['_gerrit_protocol'],
                                                               self.all_cfg['_gerrit_ip'],
                                                               self.all_cfg['_gerrit_sufix'])
        for _cmd in [query_filter + _condition for _condition in filter_condition]:
            yield _cmd

    #这里只查询gerritID，高级的功能留给 ssh 的接口，因为 ssh 接口不支持 "5min内" 这样的时间条件限制
    #而且由ssh查询，查询的结果更为详细和健全
    def _query(self):
        all_gerrit_ids = []
        for _cmd in self.gen_query_cmd():
            myrun = shell(_cmd)
            out, err, return_code = myrun.call_shell()
            if not err and len(err) ==0 and return_code ==0:
                _tmp = json.loads(out[4:])  #返回了一个list，list是某一个查询命令输出的结果
                for each_result in _tmp:
                    all_gerrit_ids.append(each_result['_number'])
        print "共查询到%s个gerrit提交满足条件..." % len(all_gerrit_ids)
        #print all_gerrit_ids
        return all_gerrit_ids

