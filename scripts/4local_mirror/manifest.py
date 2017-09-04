#!/usr/bin/python
# _*_ coding=utf-8 _*_

from xml.dom import minidom

class ManifestParser:

  def __init__(self, manifest_file):
    self.manifest_file = manifest_file

  def get_attrvalue(self, node, attrname):
    return node.getAttribute(attrname) if node else ''

  def get_xmlnode(self, node, name):
    return node.getElementsByTagName(name) if node else []
    
  def get_element_nodes(self, element):
    doc = minidom.parse(self.manifest_file)
    root = doc.documentElement
    element_nodes = self.get_xmlnode(root, element)
    return element_nodes

  def get_default_version_remote(self):
    default_nodes = self.get_element_nodes('default')
    if len(default_nodes) != 1:
      print 'Please provide a stanard default.xml'
    node = default_nodes[0]
    default_version = self.get_attrvalue(node, 'revision').encode('utf-8','ignore')
    default_remote = self.get_attrvalue(node, 'remote').encode('utf-8','ignore')
    return default_version, default_remote

  def get_remotes(self):
    remotes_dic = {}
    remotes = self.get_element_nodes('remote')
    for remote in remotes:
      remote_name = self.get_attrvalue(remote, 'name').encode('utf-8','ignore')
      remote_path = self.get_attrvalue(remote, 'fetch').encode('utf-8','ignore')
      remotes_dic[remote_name] = remote_path
    return remotes_dic

  def get_clone_list(self):
    clone_list = []
    _, default_remote = self.get_default_version_remote()
    remotes_dic = self.get_remotes()
    project_nodes = self.get_element_nodes('project')
    for node in project_nodes:
      name_value = self.get_attrvalue(node, 'name').encode('utf-8','ignore')
      remote_value = self.get_attrvalue(node, 'remote').encode('utf-8','ignore')
      if remote_value == '':
        remote_vaule = default_remote
      clone_path = '%s%s' % (remotes_dic[remote_value], name_value)
      clone_list.append(clone_path)
    return clone_list

  def get_path_name_dic(self):
    path_name_dic = {}
    project_nodes = self.get_element_nodes('project')
    for node in project_nodes:
      path_value = self.get_attrvalue(node, 'path').encode('utf-8','ignore')
      name_value = self.get_attrvalue(node, 'name').encode('utf-8','ignore')
      if path_value == '':
        path_value = name_value
      path_name_dic[path_value] = name_value
    return path_name_dic
  
  def get_path_version_dic(self):
    path_version_dic = {}
    project_nodes = self.get_element_nodes('project')
    for node in project_nodes:
      path_value = self.get_attrvalue(node, 'path').encode('utf-8','ignore')
      name_value = self.get_attrvalue(node, 'name').encode('utf-8','ignore')
      reversion_value = self.get_attrvalue(node, 'revision').encode('utf-8','ignore')
      if path_value == '':
        path_value = name_value
      if reversion_value == '':
        reversion_value = self.default_version
      path_version_dic[path_value] = reversion_value
    return path_version_dic 
