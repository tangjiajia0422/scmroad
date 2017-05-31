#!/usr/bin/python
# coding:utf8

from xml.dom import minidom

class ManifestParser:

  def __init__(self, manifest_file):
    self.manifest_file = manifest_file
    self.default_version = ''
    self.path_name_dic = {}
    self.path_version_dic = {}
    self.get_default_version()

  def get_attrvalue(self, node, attrname):
    return node.getAttribute(attrname) if node else ''

  def get_xmlnode(self, node, name):
    return node.getElementsByTagName(name) if node else []
    
  def get_element_nodes(self, element):
    doc = minidom.parse(self.manifest_file)
    root = doc.documentElement
    element_nodes = self.get_xmlnode(root, element)
    return element_nodes

  def get_default_version(self):
    default_nodes = self.get_element_nodes('default')
    if len(default_nodes) != 1:
      print 'Please provide a stanard default.xml'
    node = default_nodes[0]
    self.default_version = self.get_attrvalue(node, 'revision').encode('utf-8','ignore')

  def get_path_name_dic(self):
    project_nodes = self.get_element_nodes('project')
    for node in project_nodes:
      path_value = self.get_attrvalue(node, 'path').encode('utf-8','ignore')
      name_value = self.get_attrvalue(node, 'name').encode('utf-8','ignore')
      if path_value == '':
        path_value = name_value
      self.path_name_dic[path_value] = name_value
    return self.path_name_dic
  
  def get_path_version_dic(self):
    project_nodes = self.get_element_nodes('project')
    for node in project_nodes:
      path_value = self.get_attrvalue(node, 'path').encode('utf-8','ignore')
      name_value = self.get_attrvalue(node, 'name').encode('utf-8','ignore')
      reversion_value = self.get_attrvalue(node, 'revision').encode('utf-8','ignore')
      if path_value == '':
        path_value = name_value
      if reversion_value == '':
        reversion_value = self.default_version
      self.path_version_dic[path_value] = reversion_value
    return self.path_version_dic 
