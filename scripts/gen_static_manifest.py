#!/usr/bin/python
# -*- coding=utf-8 -*-
#
# 2015.11.24 Init
# 2015.12.01 Add query remote head from gerrit
# 2015.12.03 Add query local workspace
# 2016.04.03 Fix for prefix bug
#
# Purpose:
#        To generate static manifest

"""usage: %prog -l . -o local-static.xml (query in local workspace)
          %prog -l . -m default.xml -o local-static.xml (query in local workspace)
          %prog -u "http://192.168.65.19:8080" -b TS-CMCC-CB-REL -n tang_jiajia -m ".repo/manifest.xml" -o remote-static.xml -p "PREFIX_PROJECTS" (query by 'git ls-remote tang_jiajia@192.168.65.19:29418/ts/platform/frameworks/av refs/heads/ts-dev')
"""
import os
import sys
import argparse
import urllib2
from xml.dom import minidom
from xml.dom.minidom import Document
from xml.etree import ElementTree as ET
from subprocess import PIPE
from subprocess import Popen

def die(error_msg):
  print error_msg
  sys.exit()
  
def get_ssh_info(gerrit_url):
  opener = urllib2.build_opener()
  req = urllib2.Request('%s/ssh_info' % (gerrit_url))
  req.get_method = lambda: 'GET'
  response = opener.open(req)
  ssh_info = response.read()
  ip = ssh_info.split()[0]
  port = ssh_info.split()[1]
  return (ip, port)

def get_name_path_version_remote(each_project):
  project_name = each_project.get("name")
  project_path = each_project.get("path")
  if not project_path:
    project_path = project_name
  default_version = each_project.get("version")
  default_remote = each_project.get("remote")
  return project_name, project_path, default_version, default_remote

#def static_manifest_gen(out_manifest, manifest_file, gerrit_user, gerrit_url, local_path, project_prefix=None):
def static_manifest_gen(local_path, branch, gerrit_url, gerrit_user, manifest_file, project_prefix, out_manifest):
  os_sep = os.sep
  # prefix r is means keep origin string, no escape chars.
  # r'\tt', the string is '\tt', if no r, this string means TAB+t.
  defalut_manifest = r'.repo/manifest.xml'
  abs_path = os.path.abspath(local_path) if local_path is not None else ""
  if manifest_file is None:
    manifest_file = "%s%s%s" % (abs_path, os_sep, defalut_manifest)
  if not os.path.isfile(manifest_file):
    print "Manifest is None"
    return -1
  try:
    tree = ET.parse(manifest_file)
    root = tree.getroot()
    result_fail=[]
    #for each_project in tree.findall('project'):
    for each_project in root.iter('project'):
      project_name, project_path, default_version, default_remote = get_name_path_version_remote(each_project)
      # query from gerrit
      if not local_path and gerrit_url:
        (gerrit_ip, gerrit_port) = get_ssh_info(gerrit_url)
        ls_remote_command=[]
        gerrit_remote = \
             "ssh://%s@%s:%s/%s/%s" % (gerrit_user, gerrit_ip, gerrit_port, project_prefix, project_name) \
             if project_prefix is not None \
             else "ssh://%s@%s:%s/%s" % (gerrit_user, gerrit_ip, gerrit_port, project_name)
        if not default_version:
          ls_remote_command = ['git','ls-remote', gerrit_remote, default_version]
        if branch:
          ls_remote_command = ['git','ls-remote', gerrit_remote, 'refs/heads/'+ branch]
        print ls_remote_command
        p = Popen(ls_remote_command, shell=False, stdout=PIPE, stderr=PIPE)
        output, errmsg = p.communicate()
        if len(errmsg) > 0:
          result_fail.append(project_name)
          continue
        if len(output) > 0:
          remote_head = output.splitlines()
          print remote_head
          each_project.set('revision', remote_head[0].split()[0].strip())
      # query from local HEAD
      else:
        project_abs_path = "%s%s%s" % (abs_path, os_sep, project_path)
        if os.path.exists(project_abs_path):
          os.chdir(project_abs_path)
          ls_head_command = ['git', 'log', '-1', '--format=%H']
          p = Popen(ls_head_command, shell=False, stdout=PIPE, stderr=PIPE)
          head_sha1, errmsg = p.communicate()
          print "tangjiajia", head_sha1
          each_project.set('revision', head_sha1.strip('\n')) if len(head_sha1) > 0 else each_project.set('revision', default_version)
          os.chdir(abs_path)
        else:
          result_fail.append(project_path)
          continue
          print "Can not find: %s" %(project_path)
    tree.write(out_manifest, encoding="utf-8", xml_declaration=True, method="xml")
  except:
    print "Can not parse file %s" % (manifest_file)
  finally:  
    #root.write(out_manifest, encoding="utf-8", xml_declaration=True, method="xml")
    print "Failed projects:", result_fail

# Refer http://stackoverflow.com/questions/5165415/python-argparse-subcommand-with-dependency-and-conflict
# -l should be depart from ALL other arguments, use alone.
# parser.add_mutually_exclusive_group can only deal with "-a | -b", but can not be "-a | [-b -c -d]"
class VerifyNoLocal(argparse.Action):
  def __call__(self, parser, args, values, option_string=None):
    if getattr(args, 'local') and getattr(args, 'output'):
      parser.error('"-l local-path" should be used with -o output, no more args!')
    #if getattr(args, 'url') is None or getattr(args, 'branch') is None or getattr(args, 'user') is None or getattr(args, 'manifest') is None or getattr(args, 'output') is None or getattr(args, 'prefix') is None:
    #  parser.error('-u -b -n -m -o -p should be used together!')
    setattr(args, self.dest, values)

class VerifyOnlyLocal(argparse.Action):
  def __call__(self, parser, args, values, option_string=None):
    if getattr(args, 'url') is not None:
      parser.error('--url should not be used with -l')
    if getattr(args, 'branch') is not None:
      parser.error('--branch should not be used with -l')
    if getattr(args, 'user') is not None:
      parser.error('--user should not be used with -l')
    if getattr(args, 'output') is not None:
      parser.error('--output should not be used with -l')
    if getattr(args, 'prefix') is not None:
      parser.error('--prefix should not be used with -l')
    setattr(args, self.dest, values)

def main():
  parser = argparse.ArgumentParser(prog='PROG') 
  parser.add_argument('-v', '--verbose', help='verbose', action='store_true', default=False)

  group_root = parser.add_mutually_exclusive_group()
  group_root.add_argument('-l', '--local', action=VerifyOnlyLocal,
                    help='Parser from local-path.')
  group_remote = group_root.add_argument_group()
  group_remote.add_argument('-u', '--url', action=VerifyNoLocal,
                  help='The gerrit url.')
  group_remote.add_argument('-b', '--branch', action=VerifyNoLocal,
                  help='Branch name, used to query from gerrit.')
  group_remote.add_argument('-n', '--user', action=VerifyNoLocal, 
                  help='The gerrit username')
  group_remote.add_argument('-m', '--manifest', action=VerifyNoLocal,
                  help='The none static manifest')
  group_remote.add_argument('-o', '--output', action=VerifyNoLocal,
                  help='Output static manifest')
  group_remote.add_argument("-p", '--prefix', action=VerifyNoLocal,
                   help='Project prefix.')
  args = parser.parse_args()
  local_path = args.local
  branch = args.branch
  gerrit_url = args.url
  gerrit_user = args.user
  manifest = args.manifest
  out_manifest = args.output
  project_prefix = args.prefix

  print "local_path=%s; branch=%s; gerrit_url=%s; gerrit_user=%s; manifest=%s; out_manifest=%s; project_prefix=%s" % (local_path, branch, gerrit_url, gerrit_user, manifest, out_manifest, project_prefix)
  defalut_manifest = r'.repo/manifest.xml' 
  #static_manifest_gen(out_manifest, manifest_file, gerrit_user, gerrit_url, local_path, project_prefix):
  static_manifest_gen(local_path, branch, gerrit_url, gerrit_user, manifest, project_prefix, out_manifest)

if __name__ == '__main__':
  main()
