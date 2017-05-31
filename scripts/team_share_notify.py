#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import datetime, sys
import smtplib, email.utils
from email.mime.text import MIMEText

ori_first_c = [2, 6, 10, 14, 18, 22, 27, 31, 36, 40, 44, 49]
first_c = [x-1 for x in ori_first_c]
second_c = [x+1 for x in first_c]
third_c = [x+2 for x in first_c]

total_list = {'account1': first_c, 'account3': second_c, 'account5': third_c,
              'account2': first_c, 'account4': second_c, 'account6': third_c}
#获取当前日期是一年的第几周，是星期几。返回值是一个元组(2017,19,1)
curr_year, curr_week_num, curr_day_of_week = datetime.datetime.now().isocalendar()
#提前一周的周一发邮件
candidate_day_of_week = 1

_email_notify_body = '''
           <p><b>请本周内准备好下周团队内部分享的主题, 及文档!</b><br/>
              &nbsp;&nbsp;&nbsp;&nbsp;文档上传至 <a href="https://192.168.65.12:8070/websvn/directoryContent.jsp?location=cm&url=TMI%2F%E5%9B%A2%E9%98%9F%E5%9F%B9%E8%AE%AD%E7%AE%A1%E7%90%86%2F''' + str(curr_year) + '''">TMI/团队培训管理/''' + str(curr_year) + '''</a></p>
           <p><b>可选主题不限:</b><br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一个命令的高级使用;<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一段程序代码;<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一个工作中遇到的问题的发生情况，解决以及避免的方法<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一个stackoverflow上的问题和解答<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一个让你事半功倍的工具<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一篇文章/博客(前瞻,成熟方案介绍,技巧,guide,文献,理论)<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一本书中的某一章节<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;一个idea(不要太天马行空)<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;任何一个你觉得团队可以改进的地方<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;已有脚本中的潜在bug<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;....其他任意....<br/>
           </p>
           <p><b>详细计划, 请点击: </b><a href="http://192.168.67.56:8000/mtcl0d4pvwvb">EtherCalc-Sharing</a></p>
                     '''
_email_notify_title = '''下周分享提醒(赠人玫瑰,手留余香)'''
email_account, _pwd = 'FROM_ACCOUNT', 'FROM_ACCOUNT_PWD'
email_suffix, mail_server = 'example.com', 'mail.example.com'
email_from = '{}@{}'.format(email_account, email_suffix)
boss_account = 'MY_BOSS_ACCOUNT'
boss_email = '{}@{}'.format(boss_account, email_suffix)

def need_sendmail(candidate_week_list):
    if curr_week_num in candidate_week_list and curr_day_of_week == candidate_day_of_week:
        return True
    return False

def get_mail_tolist():
    result = []
    for _coreid in total_list:
        _candidate_week_list = total_list[_coreid]
        if need_sendmail(_candidate_week_list):
            result.append(_coreid)
    return result

def send_email(_to_list):
    if not _to_list:
        print 'Not need to reminder~~'
        sys.exit(-1)
    to_list = ['{}@{}'.format(x, email_suffix) for x in _to_list]
    email_body = '<p>Dear %s:</p> %s' % (', '.join(_to_list), _email_notify_body)
    msg = MIMEText(email_body, 'html', 'utf-8')
    #这里的To, From, Subject是显示在邮件的整体的Head里的，缺少则标题显示不完整
    #这里的To, From是可以起别名的,比如boss_account可以是my_boss_name
    msg['To'] = email.utils.formataddr((boss_account, boss_email))
    msg['Cc'] = ', '.join(to_list)
    msg['From'] = email.utils.formataddr((email_account, email_from))
    msg['Subject'] = _email_notify_title
    server = smtplib.SMTP(mail_server)
    server.set_debuglevel(True)
    try:
        server.ehlo()
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()
        server.login(email_account, _pwd)
        server.sendmail(email_from, to_list, msg.as_string())
    except:
        sys.exit(-1)
    finally:
        server.quit()

if __name__ == '__main__':
    send_email(get_mail_tolist())

