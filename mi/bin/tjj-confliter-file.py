#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import subprocess
import argparse

def istext(filepath):
    file_cmd = "file -b --mime-type %s" % (filepath)
    sed_cmd = "sed 's#/.*##'"
    file_proc = subprocess.Popen(file_cmd, shell=True, stdout=subprocess.PIPE)
    sed_result = subprocess.check_output(sed_cmd, shell=True, stdin=file_proc.stdout)
    file_proc.wait()

    return 'text' == sed_result.rstrip()

def info(msg):
    print('\033[0;32;40m%s' % msg.strip())

def main():
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-f', '--conflictfile', help='需要鉴定文件类型的文件列表文件')
    parser.add_argument('-p', '--curpath', help='当期在path路径下调用脚本')

    args = parser.parse_args()
    cfile = args.conflictfile
    curpath = args.curpath

    textfiles=[]
    binaryfiles=[]
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    with open(cfile) as f:
        for _file in f.readlines():
            abs_file_path = '%s/%s' % (curpath, _file)
            #if istext(abs_file_path):
            if is_binary_string(open(abs_file_path.rstrip(), 'rb').read(1024)):
                textfiles.append(_file)
            else:
                binaryfiles.append(_file)

    info("################################# %s BIN files ################################" % (str(len(binaryfiles))))
    [info(x) for x in binaryfiles]
    info("")
    info("################################ %s ASCII files ###############################" % (str(len(textfiles))))
    [info(x) for x in textfiles]

if __name__ == '__main__':
    main()
