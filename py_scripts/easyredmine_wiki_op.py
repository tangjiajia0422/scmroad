#!/usr/bin/env python
# coding=utf8
#
# Author by tang_jiajia@163.com
#
# Used to update easyredmine wiki page for given project
#

import sys
import os
import argparse
import urllib2
import urllib
import cookielib
from xml.etree import ElementTree as ET
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.authenticity_token = ""

  def handle_starttag(self, tag, attrs):
    if tag == "input":
      if len(attrs) == 0: pass
      else:
        for (variable, value)  in attrs:
          if variable == 'name' and value == 'authenticity_token':
            self.authenticity_token = dict(attrs)['value']

class EasyRedmineOpt:
  def __init__(self, er_wiki_content, er_api_key, er_username, er_password, er_project_id, er_wiki_title):
    self.er_wiki_content = er_wiki_content
    self.er_api_key = er_api_key
    self.er_username = er_username
    self.er_password = er_password
    self.er_project_id = er_project_id
    self.er_wiki_title = er_wiki_title 
    self.login_url = 'http://c.ts.com/login?back_url=http://c.ts.com:3000/'
    self.project_page = 'http://c.ts.com/projects/%s.xml' % (er_project_id)
    self.project_memberships = 'http://c.ts.com/projects/%s/memberships.xml' % (er_project_id)
    self.project_release_main_wiki_page = 'http://c.ts.com/projects/%s/wiki/Releases.xml?key=%s' % (er_project_id, er_api_key)
    #Bugfix release notes在redmine的url链接中首字母是大写的，而且'.'在url中会被自动删除
    #因此本来http://c.ts.com/projects/3831/wiki/msm8998-la1.1-2017-03-07-WEEK10-2-0 需要转成url：
    #http://c.ts.com/projects/3831/wiki/Msm8998-la11-2017-03-07-WEEK10-2-0
    url_er_wiki_title = er_wiki_title[0].upper() + er_wiki_title[1:]
    url_er_wiki_title = ''.join(url_er_wiki_title.split('.'))
    self.project_release_sub_wiki_page = 'http://c.ts.com/projects/%s/wiki/%s.xml?key=%s' % (er_project_id, url_er_wiki_title, er_api_key)
    self.opener = self.get_login_opener()
  
  def get_cookie_authenticity_token(self):
    opener = urllib2.build_opener()
    req = urllib2.Request(self.login_url)
    req.get_method = lambda: 'GET'
    response = opener.open(req)
    #获得首次访问时，服务器下发的cookie
    login_cookie = response.headers.get('Set-Cookie')
    login_cookie_value = login_cookie.split(';')[0]
    #从返回的登陆页面获得隐藏的表单
    mhp = MyHTMLParser()
    mhp.feed(response.read())
    login_authenticity_token = mhp.authenticity_token
    if login_cookie_value and login_authenticity_token:
      return login_cookie_value, login_authenticity_token
      
  #获得包含登陆成功的cookie的opener对象
  def get_login_opener(self):
    login_cookie_value, authenticity_token = self.get_cookie_authenticity_token()
    login_post_headers = {
                   'Connection': 'keep-alive',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/32.0.1700.107 Chrome/32.0.1700.107 Safari/537.36',
                   'Cookie': login_cookie_value
    }
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    postdata = {"username":self.er_username, "password":self.er_password, "authenticity_token": authenticity_token,  "login": ''}
    postdata_encoded = urllib.urlencode(postdata)
    req = urllib2.Request(self.login_url, postdata_encoded, headers=login_post_headers)
    req.get_method = lambda: 'POST'
    response = opener.open(req)
    return opener
      
  #查询项目基本信息
  def get_project_info(self, info_page=None):
    #默认是项目主页内容
    page = info_page if info_page is not None else self.project_page
    print "Try to get %s ..." % (page)
    proj_info_req = urllib2.Request(page, urllib.urlencode({"key": self.er_api_key}))
    proj_info_req.get_method = lambda: 'GET'
    try:
      proj_info_resp = self.opener.open(proj_info_req)
      return proj_info_resp.read()
    except:
      print "Unauthorized, plase check you uername and password first!"
      
  def get_project_wiki_content(self, project_main=True):
    if project_main:
      wiki_page = self.project_release_main_wiki_page
    else:
      wiki_page = self.project_release_sub_wiki_page
    print "** Try to get %s **" % (wiki_page)
    req = urllib2.Request(wiki_page)
    req.get_method = lambda: 'GET'
    response = self.opener.open(req)
    return response.read()
  
  def create_wiki_content(self, project_main=True, wiki_content=None):
    #如果有输入的字符串，就不用从文件里读取了
    if not wiki_content:
      wiki_file = open(self.er_wiki_content, 'r')
      wiki_content = wiki_file.read()
    self.update_wiki_content(project_main=project_main, xml_content=wiki_content)

  def update_wiki_content(self, project_main=True, xml_content=None):
    if project_main:
      wiki_page = self.project_release_main_wiki_page
    else:
      wiki_page = self.project_release_sub_wiki_page
    headers = {
            'Content-Type': 'application/xml'
    }
    print "Update wiki: %s ..." % (wiki_page)
    req = urllib2.Request(wiki_page, data=xml_content, headers=headers)
    req.get_method = lambda: 'PUT'
    response = self.opener.open(req)

############################################
#
# %prog -f 'filepath' -k 'apikey' -n 'username' -p 'password' -d 'projectid' -t 'wikititle'
#
############################################
def gen_xml_content(title, parent_title, xml_text):
  xml_wiki_content = '\
  <wiki_page>\n\
    <title>%s</title>\n\
    <parent title="%s"/>\n\
    <text>%s</text>\n\
  </wiki_page>\
  ' % (title, parent_title, xml_text)
  return xml_wiki_content

def main():
  parser = argparse.ArgumentParser(prog='PROG')
  #需要更新的wiki页的主体部分内容。
  parser.add_argument('-f', '--wikibody', required=True, help='Only the content for the wiki page, no need xml formated.')
  #需要的apikey，在easyredmine的个人设置中可以找到，这个key就是帐号的身份证。
  parser.add_argument('-k', '--apikey', required=True, help='My easyredmine api key.')
  #登陆easyredmine的帐号。
  parser.add_argument('-n', '--username', required=True, help='Username to login easyredmine.')
  #登陆easyredmine的密码。
  parser.add_argument('-p', '--password', required=True, help='Password to login easyredmine.')
  #project ID，只能指定有权限的项目
  parser.add_argument('-d', '--projectid', required=True, help='The project ID, which is the parenet for the wiki page.')
  #wiki page标题
  parser.add_argument('-t', '--title', required=True, help='The title of the wikipage, also part of the url.')

  args = parser.parse_args()
  er_wiki_content = args.wikibody
  er_api_key = args.apikey
  er_username = args.username
  er_password = args.password
  er_project_id = args.projectid
  er_wiki_title = args.title

  myEasyRedmineOpt = EasyRedmineOpt(er_wiki_content, er_api_key, er_username, er_password, er_project_id, er_wiki_title)
  #myEasyRedmineOpt.get_project_info()
  #print "List all project memebers ========"
  #memberships = myEasyRedmineOpt.get_project_info(myEasyRedmineOpt.project_memberships)
  #for members in ET.fromstring(memberships).findall('membership'):
  #  print members.find('user').get('name')
  
  #创建/更新项目release的主wiki页，这页是每个版本的索引
  #http://c.ts.com/projects/%s/wiki/Releases.xml
  try:
    #在如果第一次查询主wiki页，失败，说明是第一次创建，进入except块
    current_wiki_content = myEasyRedmineOpt.get_project_wiki_content(project_main=True)
    #把每天的release的wiki页更新到Release标签下，方便寻找
    parsed_content = ET.fromstring(current_wiki_content)
    current_wiki_page_text = parsed_content.find('text').text
    #如果此版本已经在releases页面里，那么就不需要添加该版本的索引，直接更新sub页的内容即可
    if er_wiki_title not in current_wiki_page_text:
      new_wiki_page_text = current_wiki_page_text.replace('h2. ', 'h2. [[%s]]\n' % (er_wiki_title))
      new_wiki_page_xml = gen_xml_content('releases', 'wiki', new_wiki_page_text)
      myEasyRedmineOpt.update_wiki_content(project_main=True, xml_content=new_wiki_page_xml)
  except:
    #第一次，创建
    first_main_wiki_page_xml = gen_xml_content('releases', 'wiki', 'h1. Releases \n\nh2. [[%s]] \n' % (er_wiki_title))
    myEasyRedmineOpt.create_wiki_content(project_main=True, wiki_content=first_main_wiki_page_xml)

  #创建每天的release的wiki页
  myEasyRedmineOpt.create_wiki_content(project_main=False)

if __name__ == '__main__':
  main()
