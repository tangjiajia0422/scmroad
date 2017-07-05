#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import time, datetime, os, sys
import ConfigParser
from manifest import ManifestParser
import subprocess

class utils:
    def __init__(self, script_path):
        self.patch_out_file = '.commits.local'
        self.script_path = script_path

    def cfg_parser(self):
        cfg_parser = ConfigParser.ConfigParser()

        cfg_parser.read('%s/%s' % (self.script_path, 'local.cfg'))
        all_cfg = {}

        def first_verify_set(_part, _tmp, canbe_none=True):
            _tmp_src = cfg_parser.get(_part, _tmp)
            _tmp_list = _tmp_src.split()
            if canbe_none:
                if len(_tmp_list) == 0: all_cfg[_tmp] = ''
                elif len(_tmp_list) == 1: all_cfg[_tmp] = _tmp_list[0]
                elif len(_tmp_list) > 1: self.print_error('错误: %s最多只能赋一个值!' % (_tmp))
            else:
                if len(_tmp_list) != 1:
                    self.print_error('错误: %s必须只能赋一个值!' % (_tmp))
                else: all_cfg[_tmp] = _tmp_list[0]

        first_verify_set("source", "SOURCE_STATIC_MANIFEST")
        first_verify_set("source", "SOURCE_BASE_STATIC_MANIFEST")

        first_verify_set("source", "SOURCE_ABS_PATH", False)
        if not all_cfg["SOURCE_STATIC_MANIFEST"]:
            first_verify_set("source", "SOURCE_BRANCH")
        else: all_cfg["SOURCE_BRANCH"] = all_cfg["SOURCE_STATIC_MANIFEST"].split('/')[-1]
        if not all_cfg["SOURCE_BASE_STATIC_MANIFEST"]:
            first_verify_set("source", "SOURCE_BASE_BRANCH", False)
        else: all_cfg["SOURCE_BASE_BRANCH"] = all_cfg["SOURCE_BASE_STATIC_MANIFEST"].split('/')[-1]

        first_verify_set("target", "TARGET_ABS_PATH", False)

        _source_isolated_repo = cfg_parser.get("source", "SOURCE_ISOLATED_REPO")
        all_cfg['SOURCE_ISOLATED_REPO'] = _source_isolated_repo.split()

        _committer_email_list = cfg_parser.get("patch_condition", "COMMITTER_EMAIL_LIST")
        all_cfg['COMMITTER_EMAIL_LIST'] = '\|'.join(_committer_email_list.split())

        all_cfg['TARGET_BACKUP_BRANCH'] = 'TARGET_BACKUP_BRANCH'

        return self.pre_verify_set(all_cfg)

    def pre_verify_set(self, all_cfg):
        tmp_source_abs_path = all_cfg['SOURCE_ABS_PATH']
	if not tmp_source_abs_path:  #SOURCE_ABS_PATH为空，退出
            self.print_error('错误: 源路径(local.cfg:SOURCE_ABS_PATH)不可以为空!')
        else:
            defalut_manifest = '%s/%s' % (tmp_source_abs_path, '.repo/manifest.xml')
            if os.path.exists(defalut_manifest):
                manifest = ManifestParser(defalut_manifest)
                if not all_cfg['SOURCE_BRANCH']:
                    all_cfg['SOURCE_BRANCH'] = manifest.get_default_version()
            else:
                self.print_error('错误: 不能找到manifest文件: %s/%s' % (tmp_source_abs_path, '.repo/manifest.xml'))

            tmp_source_isolated_repo = all_cfg['SOURCE_ISOLATED_REPO']
            tmp_source_isolated_repo = [x[:len(x)-1] if x.endswith('/') else x for x in tmp_source_isolated_repo]
            if tmp_source_isolated_repo and len(tmp_source_isolated_repo) > 0:  #SOURCE_ISOLATED_REPO不为空，忽略.repo/manifest.xml
                for _repo in tmp_source_isolated_repo:
                    if not os.path.exists('%s/%s' % (tmp_source_abs_path, _repo)):
                        self.print_error('错误: 不能找到仓库: %s/%s，请在local.cfg中设置正确的SOURCE_ISOLATED_REPO' % (tmp_source_abs_path, _repo))
                all_cfg['SOURCE_ISOLATED_REPO'] = tmp_source_isolated_repo
            else:
                path_name_dic = manifest.get_path_name_dic()
                #需要剔除掉manifest中path是'.'的仓库，这在路径处理的时候会出错
                all_cfg['SOURCE_ISOLATED_REPO'] = [path_name_dic[x] if x == '.' else x for x in path_name_dic.keys()]
            all_cfg['PATCH_OUT_PATH'] = '%s/%s_%s_%s' % \
                  (tmp_source_abs_path, all_cfg['SOURCE_BASE_BRANCH'].replace('/', '_'), all_cfg['SOURCE_BRANCH'].replace('/', '_'), 'patch_out')
        return all_cfg

    def print_error(self, msg, to_exit=True, is_error=True):
        if is_error:
            print('\033[1;31;40m%s' % msg)
        else:
            print('\033[0;32;40m%s' % msg)
        if to_exit:
            sys.exit(-1)

    def readable_timestamp(self, timestamp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(timestamp)))

    def readable_today(self):
        return datetime.date.today()

    def print_defined_env(self, all_cfgs):
        max_key_len = max([len(x) for x in all_cfgs])
        for key, value in all_cfgs.items():
            print "{f_key:>{key_len}} : {f_value:<}".format(f_key=key, key_len=max_key_len, f_value=value)

    def if_branch_exist(self, _path, branch_or_tag_name, willexit=True):
        #完全匹配，如果branch和tag完全重名，使用branch！
        _find_branch_cmd = 'git branch -a | grep -w -E "[[:blank:]]%s|^%s"' % (branch_or_tag_name, branch_or_tag_name)
        _find_tag_cmd = 'git tag | grep -w -E "[[:blank:]]%s|^%s"' % (branch_or_tag_name, branch_or_tag_name)
        _branch_result, _, _ = shell(_find_branch_cmd).call_shell(False, True)
        _tag_result, _, _ = shell(_find_tag_cmd).call_shell(False, True)
        if _branch_result or _tag_result:
            return branch_or_tag_name

        #完整匹配，如果branch名有前缀，像remotes/caf/brancha
        _find_branch_cmd = 'git branch -a | grep -E ".+/%s$" | sort | tail -1' % branch_or_tag_name
        _branch_result, _, _ = shell(_find_branch_cmd).call_shell(False, True)
        if _branch_result:
            return _branch_result.strip()
        self.print_error('错误: %s不存在分支: %s' % (_path, branch_or_tag_name), willexit)
        return ''

    def clean_empty_folders(self, _top_path):
        if os.path.isdir(_top_path):
            for p in os.listdir(_top_path):
                d = os.path.join(_top_path, p)
                if os.path.isdir(d):  
                    clean_empty_folders(d)
                elif os.path.isfile(d):
                    if os.path.getsize(d) == 0:
                        os.remove(d)
        if not os.listdir(_top_path):
            os.rmdir(_top_path)

class shell:
    def __init__(self, _cmd):
        self.utils = utils('')
        if _cmd:
            self._cmd = _cmd
        else:
            self.utils.print_error('命令为空，没有命令可以执行...')

    def call_shell(self, willprint=True, exit=True):
        if willprint:
           print 'Executing shell cmd >>> ', self._cmd
        pipe = subprocess.Popen("%s" % self._cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errmsg = pipe.communicate()
        popen_returncode = pipe.returncode
        if not errmsg and len(errmsg) != 0 and popen_returncode != 0:
            if exit:
                self.utils.print_error(errmsg[0:200])
            #else:
            #    self.utils.print_error('跳过错误: %s' % errmsg[0:200], False) #截取err的前200个字符
        return output, errmsg, popen_returncode
