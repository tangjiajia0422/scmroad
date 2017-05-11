#!/usr/bin/env python
# _*_ coding=utf-8 _*_

from gerrit_query import gerrit_query
from call_shell import shell
from utils import utils
import json, os

class ssh_gerrit_query(gerrit_query):

    def __init__(self, query_method='ssh'):
        super(ssh_gerrit_query, self).__init__()
        self.all_cfg['_query_method'] = query_method

    '''
    Gerrit document:
    ssh -p 29418 ACCOUNT@HOST gerrit query --format=JSON --commit-message --current-patch-set --comments --all-reviewers --files ID
    记录的字段：
{
    "allReviewers": [
        {
            "email": "account1@example.com", 
            "username": "account1"
        }, 
        {
            "email": "account2@example.com", 
            "username": "account2"
        }
    ], 
    "branch": "msm8998-la1.1", 
    "comments": [
        {
            "message": "Uploaded patch set 1.", 
            "reviewer": {
                "email": "account2@example.com", 
                "username": "account2"
            }, 
            "timestamp": 1493368634
        }, 
        {
            "message": "Patch Set 1: Verified-1 Code-Review-2", 
            "reviewer": {
                "email": "account2@example.com", 
                "username": "account2"
            }, 
            "timestamp": 1493369435
        }, 
        {
            "message": "Abandoned", 
            "reviewer": {
                "email": "account2@example.com", 
                "username": "account2"
            }, 
            "timestamp": 1493773364
        }
    ], 
    "commitMessage": "Reboot device if kernel address read failed\n\nChange-Id: Icb8214982e1174ab929f5f85f89ac79fcf2d4cdf\n", 
    "createdOn": 1493368634, 
    "currentPatchSet": {
        "approvals": [
            {
                "by": {
                    "email": "account2@example.com", 
                    "username": "account2"
                }, 
                "description": "Code-Review", 
                "grantedOn": 1493369435, 
                "type": "Code-Review", 
                "value": "-2"
            }, 
            {
                "by": {
                    "email": "account2@example.com", 
                    "username": "account2"
                }, 
                "description": "Verified", 
                "grantedOn": 1493369435, 
                "type": "Verified", 
                "value": "-1"
            }
        ], 
        "author": {
            "email": "account2@example.com", 
            "username": "account2"
        }, 
        "createdOn": 1493368634, 
        "files": [
            {
                "deletions": 0, 
                "file": "/COMMIT_MSG", 
                "insertions": 9, 
                "type": "ADDED"
            }, 
            {
                "deletions": -1, 
                "file": "QcomModulePkg/Library/BootLib/BootLinux.c", 
                "insertions": 10, 
                "type": "MODIFIED"
            }
        ], 
        "isDraft": false, 
        "kind": "REWORK", 
        "number": "1", 
        "parents": [
            "bd2ee9c670c57e880feb23435d8af6ee8687eede"
        ], 
        "ref": "refs/changes/60/10260/1", 
        "revision": "aaf8ed4f6ef098023da83cd948e85b48d90ef59d", 
        "sizeDeletions": -1, 
        "sizeInsertions": 10, 
        "uploader": {
            "email": "account2@example.com", 
            "username": "account2"
        }
    }, 
    "id": "Icb8214982e1174ab929f5f85f89ac79fcf2d4cdf", 
    "lastUpdated": 1493773364, 
    "number": "10260", 
    "open": false, 
    "owner": {
        "email": "account2@example.com", 
        "username": "account2"
    }, 
    "project": "8x98/abl/tianocore/edk2", 
    "status": "ABANDONED", 
    "subject": "Reboot device if kernel address read failed", 
    "url": "http://192.168.67.126:8080/10260"
}
    '''
    def gen_query_cmd(self, gerrit_id_list):
        if gerrit_id_list:
            #删掉第二行，第二行是统计输出的，因此整体输出不能作为json解析，第二行:
            #{"type":"stats","rowCount":1,"runTimeMilliseconds":9,"moreChanges":false}
            query_cmd_list = ['%s -p %s %s@%s gerrit query --format=JSON --files --commit-message --current-patch-set --comments --all-reviewers %s | sed 2d' % (self.all_cfg['_query_method'],
                                         self.all_cfg['_gerrit_ssh_port'],
                                         self.all_cfg['_gerrit_account'],
                                         self.all_cfg['_gerrit_ip'],
                                         _id) for _id in gerrit_id_list]
            print os.linesep.join(query_cmd_list)
            return query_cmd_list

    #使用ssh接口查询
    def _query(self, gerrit_id_list):
        ssh_query_result = []
        cmd_list = self.gen_query_cmd(gerrit_id_list)
        for _cmd in cmd_list:
            _out, _err, r_code = shell(_cmd).call_shell()
            _tmp = json.loads(_out)  #返回了一个字典
            ssh_query_result.append(_tmp)
        return ssh_query_result
