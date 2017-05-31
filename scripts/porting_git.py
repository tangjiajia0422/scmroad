#!/usr/bin/python
# _*_ coding=utf8 _*_

'''
用来将andorid的一个整仓库，拆成单个仓库后，保留历史记录
'''
import re, os
from call_shell import shell
from manifest import ManifestParser

SRC_WORKSPACE="/home/help/tangjiajia/android4.4.3_d531_work"
#SRC_WORKSPACE="/home/help/tangjiajia/android4.4.3_d531"
TARGET_WORKSPACE="/home/help/tangjiajia/pre-commit/new_workspace"

def get_src_commits():
    os.chdir(SRC_WORKSPACE)
    if os.path.exists('.git'):
        first_sha1, _, _ = shell('git log --no-merges --format=%H | tac').call_shell()
        return first_sha1.split()
    return None

def deal_first_commit(first_sha1):
    # 解析manifest.xml文件，默认的manifest路径是:TARGET_WORKSPACE/.repo/manifest.xml
    manifest = ManifestParser('%s/.repo/manifest.xml' % (TARGET_WORKSPACE))
    path_name_dict = manifest.get_path_name_dic()
    os.chdir(SRC_WORKSPACE)
    shell('git checkout -f %s' % (first_sha1)).call_shell()
    for each_path in path_name_dict:
        shell('mv %s/%s/* %s/%s' % (SRC_WORKSPACE, each_path, TARGET_WORKSPACE, each_path)).call_shell()

def changed_info(pre_sha1, cur_sha1):
    _files, _, _ = shell("git diff --name-status %s %s | awk '{print $2}'" % (pre_sha1, cur_sha1)).call_shell()
    _subject, _, _ = shell('git log %s --format="%s" -1' % (cur_sha1)).call_shell()
    _author, _, _ = shell('git log %s --format="%aN <%aE>" -1' % (cur_sha1)).call_shell()
    return _author, _subject, _files.split()

def find_changed_path(_file_list, path_name_dict):
    result_list = []
    for _path in path_name_dict:
        for _file in _file_list:
            if re.search(_path, _file):
                result_list.append(_path)
    return set(result_list)

def deal_other_commits(commit_sha1s):
    manifest = ManifestParser('%s/.repo/manifest.xml' % (TARGET_WORKSPACE))
    path_name_dict = manifest.get_path_name_dic()
    start=1
    while start < len(commit_sha1s):
        pre_sha1, cur_sha1 = commit_sha1s[start-1], commit_sha1s[start]
        c_author, c_subject, c_files = changed_files(pre_sha1, cur_sha1)
        changed_path = find_changed_path(c_files, path_name_dict)
        # 根据manifest中的copy规则，这两个文件放在build目录下
        if 'build.prop' in c_files:
            changed_path.add('build')
            shell("cp -fr %s/%s %s/%s" % (SRC_WORKSPACE, 'build.prop', TARGET_WORKSPACE, 'build')).call_shell()
        if 'build_d531.sh' in c_files:
            changed_path.add('build')
            shell("cp -fr %s/%s %s/%s" % (SRC_WORKSPACE, 'build_d531.sh', TARGET_WORKSPACE, 'build')).call_shell()
        for each_f in c_files:
            shell("cp -fr %s/%s %s/%s" % (SRC_WORKSPACE, each_f, TARGET_WORKSPACE, each_f)).call_shell()
        for c_path in changed_path:
            shell('cd %s/%s; git add -A; git commit -m "%s" --author="%s"' % (TARGET_WORKSPACE, c_path, c_subject, c_author)).call_shell()
        start += 1

if __name__ == '__main__':
    all_sha1 = get_src_commits()
    if all_sha1:
#        deal_first_commit(all_sha1[0])
        deal_other_commits(all_sha1)


