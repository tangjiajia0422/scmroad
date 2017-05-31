#!/usr/bin/python
# coding:utf8
#
# Author by tang_jiajia@163.com
#

'''
Compare two(old, new) manifest to find how many commits between two versions.
  manifest1 is the old daily static manifest
  manifest2 is the new daily static manifest
  If key in manifest1 but not in manifest2, means new version has removed this project
  If key in manifest2 but not in manifest1, means new version has added tis project
'''

import os
import cgi
import sys
import subprocess
import json
import argparse
from manifest import ManifestParser

reload(sys)
sys.setdefaultencoding("utf-8")

def main():
  parser = argparse.ArgumentParser(prog='PROG')
  parser.add_argument('-w', '--absolute_path', required=True, help="The work space for build.")
  parser.add_argument('-p', '--previous_manifest', required=True, help="Path of the old manifest.")
  parser.add_argument('-c', '--current_manifest', required=True, help="Path of the new manifest.")
  parser.add_argument('-s', '--gerrit_host', required=True, help="The gerrit ip to query.")
  parser.add_argument('-t', '--gerrit_port', required=True, help="The gerrit port.")
  parser.add_argument('-u', '--gerrit_user', required=True, help="The gerrit user.")
  parser.add_argument('-r', '--release_subject', required=True, help="The subject of wiki page.")
  parser.add_argument('-o', '--wiki_content_file_path', required=True, help="The output of the wiki page content.")
  args = parser.parse_args()

  absolue_path_prefix = args.absolute_path
  manifest1 = args.previous_manifest
  manifest2 = args.current_manifest
  gerrit_ip = args.gerrit_host
  gerrit_user = args.gerrit_user
  gerrit_port = args.gerrit_port
  release_subject = args.release_subject
  wiki_content_file_path = args.wiki_content_file_path
  
  wiki_content_file = open('%s' % (wiki_content_file_path), 'w+')
  wiki_content_file.writelines('<wiki_page>\n')
  wiki_content_file.writelines('<title>%s</title>\n' % (release_subject))
  wiki_content_file.writelines('<parent title="Releases"/>\n')
  wiki_content_file.writelines('<text>h1. %s \n\n' % (release_subject))

  mp1 = ManifestParser(manifest1)
  mp2 = ManifestParser(manifest2)

  mp1_path_name_dic = mp1.get_path_name_dic()
  mp2_path_name_dic = mp2.get_path_name_dic()
  mp1_path_version_dic = mp1.get_path_version_dic()
  mp2_path_version_dic = mp2.get_path_version_dic()

  new_version_removed_list_path_name = {}
  new_version_removed_list_path_version = {}
  new_version_added_list_path_name = {}
  new_version_added_list_path_version = {}

  for k_path in mp1_path_name_dic.keys():
    if k_path not in mp2_path_name_dic.keys():
      new_version_removed_list_path_name[k_path] = mp1_path_name_dic[k_path]
      new_version_removed_list_path_version[k_path] = mp1_path_version_dic[k_path]
      del(mp1_path_version_dic[k_path])
      wiki_content_file.writelines('|Deleted |%s |\n\n' % (k_path))

  for k_path in mp2_path_name_dic.keys():
    if k_path not in mp1_path_name_dic.keys():
      new_version_added_list_path_name[k_path] = mp2_path_name_dic[k_path]
      new_version_added_list_path_version[k_path] = mp2_path_version_dic[k_path]
      del(mp2_path_version_dic[k_path])
      wiki_content_file.writelines('|Added |%s |\n\n' % (k_path))

  wiki_content_file.writelines('|_.GerritID |_.Subject |_.Submitter |_.Path |_.CommitID |\n')
  #By the above filter add or removed projects, the remained project shall be the same
  if len(mp1_path_version_dic) == len(mp2_path_version_dic):
    for k_path in mp1_path_version_dic.keys():
      mp1_version = mp1_path_version_dic[k_path]
      mp2_version = mp2_path_version_dic[k_path]
      cmd_list_sha1 = 'cd %s/%s ; git log --pretty=oneline %s..%s' % (absolue_path_prefix, k_path, mp1_version, mp2_version)
      if mp1_version != mp2_version:
        cmd_list_output = subprocess.Popen(cmd_list_sha1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in cmd_list_output.stdout.readlines():
          sha1 = line[:40]
          cmd_gerrit_query = 'ssh -p %s %s@%s gerrit query --format=JSON --commit-message %s --current-patch-set | sed 2d' % (gerrit_port, gerrit_user, gerrit_ip, sha1)
          #print cmd_gerrit_query
          cmd_gerrit_result = subprocess.Popen(cmd_gerrit_query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          cmd_gerrit_output = cmd_gerrit_result.stdout.read()
          try:
            json_str = json.loads(cmd_gerrit_output)
            gerrit_id = json_str["number"]
            gerrit_url = json_str["url"]
            gerrit_subject = json_str["subject"]
            gerrit_submitter = json_str["currentPatchSet"]["uploader"]["email"]
            gerrit_path = k_path
            gerrit_sha1 = sha1
            wiki_content_file.writelines(cgi.escape('|"%s":%s |%s |%s |%s |%s |\n' % (gerrit_id, gerrit_url, gerrit_subject, gerrit_submitter, gerrit_path, gerrit_sha1)))
          except Exception,e:
            pass
  wiki_content_file.writelines('</text></wiki_page>\n')
  wiki_content_file.close()

if __name__ == '__main__':
  main()
