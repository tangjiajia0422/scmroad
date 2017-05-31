#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import argparse
from manifest import ManifestParser
from gerrit_create_projects import create_projects

def main():
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-m', '--manifest', help='The none static manifest', required=True)
    # 从参数中获取manifest文件
    args = parser.parse_args()
    manifest_file = args.manifest
    # 解析manifest.xml文件
    manifest = ManifestParser(manifest_file)
    path_name_dict = manifest.get_path_name_dic()
    # 开始创建project
    c_p = create_projects()
    c_p.create_parent_project()
    dict_success_created_project, dict_failed_created_project, dict_existed_project = c_p.create_given_projects(path_name_dict)
    print 'Failed>>>>>'
    print dict_failed_created_project
    print 'Exited>>>>>'
    print dict_existed_project

if __name__ == '__main__':
    main()
