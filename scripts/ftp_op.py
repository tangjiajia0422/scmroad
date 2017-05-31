#!/usr/bin/python
# -*- coding=utf-8 -*-
#
# Author by tang_jiajia@163.com 
#
# 2015-12-27 Init.
# 2015-12-30 Add baisc download and upload one file.
# 2016-01-06 Add download and upload folder.
# 2016-01-25 Add delete file/folder from FTP.
#

'''
Example to use:
    Upload one single file:
        %prog -r <remote> -l <local> -n <ftp-user> -p <ftp-passwd> -t <ftp-host> -u -f
        ftp_op.py -r test/a.tgz -l test/a.tgz -n slsi -p slsi123 -t 192.168.65.220 -u -f
    Download one single file:
        %prog -r <remote> -l <local> -n <ftp-user> -p <ftp-passwd> -t <ftp-host> -d -f
        ftp_op.py -r test/a.tgz -l test/a.tgz -n slsi -p slsi123 -t 192.168.65.220 -d -f
    Upload folder:
        %prog -r <remote> -l <local> -n <ftp-user> -p <ftp-passwd> -t <ftp-host> -u
        ftp_op.py -r mytest/test -l test -n slsi -p slsi123 -t 192.168.65.220 -u
    Download folder:
        %prog -r <remote> -l <local> -n <ftp-user> -p <ftp-passwd> -t <ftp-host> -d
        ftp_op.py -r test -l test -n slsi -p slsi123 -t 192.168.65.220 -d
    Delete folder or file:
        %prog -r <remote> -n <ftp-user> -p <ftp-passwd> -t <ftp-host> -D
        ftp_op.py -r test -n slsi -p slsi123 -t 192.168.65.220 -D
'''

import ftplib
import sys
import os
import argparse
import hashlib
import socket
import shutil
import StringIO

class MyFtp:
    ftp = None
    ftpHost = None

    #Constructor
    def __init__(self, host, username, passwd):
        self.ftpHost = host
        self.ftp = self.ftpconnect(host, username, passwd)

    #Destructor
    def __del__(self):
        if self.ftp:
            self.disconnect()
            self.ftp = None

    #Init ftp
    def ftpconnect(self, host, username, passwd):
        try:
            myftp = ftplib.FTP(host)
            myftp.login(username, passwd)
            return myftp
        except socket.error, socket.gaierror:
            print "Login to %s failed! username=%s, passwd=%s" % (host, username, passwd)
            sys.exit(0)

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()

    #Upload single file
    def uploadFile(self, localpath, remotepath):
        self.infoHead('upload', localpath)
        #If local file path is not a file
        if not os.path.isfile(localpath):
            return False
        local_md5 = self.getLocalMd5(localpath)
        upload_buf_size = 1024
        f = open(localpath, 'rb')
        try:
            self.ftp.storbinary('STOR ' + remotepath, f, upload_buf_size)
        except ftplib.error_perm:
            self.disconnect()
            return False
        f.close()
        remote_md5 = self.getRemoteMd5(remotepath)
        print "Local %s md5 = %s, remote %s md5 = %s" % (localpath, local_md5, remotepath, remote_md5)
        if local_md5 == remote_md5:
             return True
        return False

    #Upload folder
    def uploadFolder(self, localpath, remotepath):
        self.infoHead('upload', localpath)
        local_files = os.listdir(localpath)
        #If nothing archived in the localpath, just a empty path.
        #Start to create path
        #self.deleteFromFTP(remotepath)
        try:
            self.ftp.mkd(remotepath)
        except ftplib.error_perm:
            print 'Could not mkdir %s on ftp server' % (remotepath)
        #End to create path

        #If path is not empty
        if local_files:
            for eachFile in local_files:
                local_src = os.path.join(localpath, eachFile)
                remote_dest = os.path.join(remotepath, eachFile)
                if os.path.isdir(local_src):
                    self.uploadFolder(local_src, remote_dest)
                else:
                    self.uploadFile(local_src, remote_dest)

    #Download folder
    def downloadFolder(self, localpath, remotepath):
        self.infoHead('download', remotepath)
        #Start to check if remotepath is a dir.
        #self.ftp.dir function will print to sys.stdout, so re-define sys.stdout, then get the result.
        old_stdout = sys.stdout
        sys.stdout = new_stdout = StringIO.StringIO()
        self.ftp.dir(remotepath)
        remote_files = new_stdout.getvalue().split('\n')[:-1]
        sys.stdout = old_stdout
        #End. Already got the dir results, restore the sys.stdout.
        if remote_files:
            for eachFile in remote_files:
                meta_data_list = eachFile.split(' ')
                meta_data_isd = meta_data_list[0]
                file_name = meta_data_list[-1]
                local_file_path = os.path.join(localpath, file_name)
                remote_file_path = os.path.join(remotepath, file_name)
                #If is a dir, the meta data will be like "drwxr-xr-x ABCDEFG".
                #If is file, the meta data will be like "-rw-r--r-- ABCDEFG"
                if meta_data_isd.startswith('d') or "<dir>" in meta_data_list or "<DIR>" in meta_data_list:
                    if os.path.exists(local_file_path):
                        shutil.rmtree(local_file_path)
                    os.makedirs(local_file_path)
                    self.downloadFolder(local_file_path, remote_file_path)
                else:
                    self.downloadFile(local_file_path, remote_file_path)
        try:
            self.ftp.rmd(remotepath)
            print "Remove folder %s success!" % (remotepath)
        except ftplib.all_errors:
            print "Remove folder %s failed!" % (remotepath)

    #Download single file
    def downloadFile(self, localpath, remotepath):
        self.infoHead('download', remotepath)
        # if local_file is exist, rm
        if os.path.isfile(localpath):
            os.remove(localpath)
        if not os.path.exists(os.path.dirname(localpath)):
            os.makedirs(os.path.dirname(localpath))
        download_buf_size = 4096
        print localpath
        f = open(localpath,'w+')
        try:
            self.ftp.retrbinary('RETR ' + remotepath, f.write, download_buf_size)
        except ftplib.error_perm:
            self.disconnect()
            return False
        # The buff data will be flushed from program buffer to operating system buffer
        f.flush()
        # make sure data from operating system buffers to disk
        os.fsync(f.fileno())
        # close file descriptor
        f.close()
        local_md5 = self.getLocalMd5(localpath)
        remote_md5 = self.getRemoteMd5(remotepath)
        print "Local %s md5 = %s, remote %s md5 = %s" % (localpath, local_md5, remotepath, remote_md5)
        if local_md5 == remote_md5:
             return True
        return False

    def deleteFile(self, remotepath):
        self.infoHead('delete', remotepath)
        try:
            self.ftp.delete(remotepath)
        except ftplib.error_perm:
            print 'Could not delete file %s on ftp server' % (remotepath)
            return False
        return True

    def deleteFromFTP(self, remotepath):
        cpwd = self.ftp.pwd()
        try:
            fileList = self.ftp.nlst(remotepath)
            for eachFile in fileList:
                if os.path.split(eachFile)[1] in ('.', '..'): continue
                try:
                    self.ftp.cwd(eachFile) # if we can cwd to it, it's a folder
                    self.ftp.cwd(cpwd) # don't try a nuke a folder we're in
                    self.deleteFromFTP(eachFile)
                except ftplib.all_errors:
                    self.ftp.delete(eachFile)
            self.ftp.rmd(remotepath)
        except ftplib.all_errors:
            pass

    def infoHead(self, operation, filePath):
        if operation == 'download' or operation == 'delete':
            print 'Start to %s %s from %s ...' % (operation, filePath, self.ftpHost)
        elif operation == 'upload':
            print 'Start to %s %s to %s ...' % (operation, filePath, self.ftpHost)

    def getLocalMd5(self, localpath):
        # check local file md5 value
        ml = hashlib.md5()
        #ml.update(open(localpath, 'rb').read())
        #If RAM is not enough, 4k buffer will be more stable.
        buff_size = 4096
        fd_local = open(localpath, 'rb')
        while True:
            buf = fd_local.read(buff_size)
            if buf:
                ml.update(buf)
            else:
                break
        return ml.hexdigest()

    def getRemoteMd5(self, remotepath):
        # check remote file md5 value
        mr = hashlib.md5()
        self.ftp.retrbinary('RETR %s' % remotepath, mr.update)
        return mr.hexdigest()

def main():
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-r', '--remote_file', required=True, help='The file path on the FTP server.')
    parser.add_argument('-l', '--local_file', help='The local file path.')
    parser.add_argument('-n', '--username', required=True, help='Username to login FTP server.')
    parser.add_argument('-p', '--password', required=True, help='Password to login FTP server.')
    parser.add_argument('-t', '--host_ip', required=True, help='Host of FTP server.')
    # Default is to download or upload one single file
    parser.add_argument('-f', '--is_file', action='store_true', help='Download or upload file.')

    group_exclusive = parser.add_mutually_exclusive_group()
    group_exclusive.add_argument('-d', '--ftp_download', action='store_true', help='Download from ftp server.')
    group_exclusive.add_argument('-u', '--ftp_upload', action='store_true', help='Upload to FTP server.')
    group_exclusive.add_argument('-D', '--ftp_delete', action='store_true', help='Delete from FTP server.')

    args = parser.parse_args()
    remote_file_path = args.remote_file
    local_file_path = args.local_file
    ftp_username = args.username
    ftp_pwd = args.password
    ftp_host = args.host_ip
    d_u_file = args.is_file

    ftp_download = args.ftp_download
    ftp_upload = args.ftp_upload
    ftp_delete = args.ftp_delete

    print "remote_file_path=%s, local_file_path=%s, ftp_username=%s, ftp_pwd=%s, ftp_host=%s, d_u_file=%s, ftp_download=%s, ftp_upload=%s" % (remote_file_path, local_file_path, ftp_username, ftp_pwd, ftp_host, d_u_file, ftp_download, ftp_upload)

    # download or upload
    l_ftp = MyFtp(ftp_host, ftp_username, ftp_pwd)

    if l_ftp:
        #Download
        if ftp_download:
            if d_u_file:
                if l_ftp.downloadFile(local_file_path, remote_file_path):
                    print "%s ---> %s" % (remote_file_path, local_file_path)
            else:
                 l_ftp.downloadFolder(local_file_path, remote_file_path)
        #Upload
        if ftp_upload:
            if d_u_file:
                if l_ftp.uploadFile(local_file_path, remote_file_path):
                    print "%s ---> %s" % (local_file_path, remote_file_path)
            else:
                l_ftp.uploadFolder(local_file_path, remote_file_path)
        #Delete
        if ftp_delete:
            l_ftp.deleteFromFTP(remote_file_path)

if __name__ == '__main__':
    main()
