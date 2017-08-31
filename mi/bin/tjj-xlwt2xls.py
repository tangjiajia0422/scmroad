#!/usr/bin/env python
# _*_ coding=utf-8 _*_

from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook# http://pypi.python.org/pypi/xlrd
import xlwt                   # http://pypi.python.org/pypi/xlwt
import os, sys, argparse

parser = argparse.ArgumentParser(prog='PROG')
parser.add_argument('-r', '--row_num', required=True, help='Which row to insert')
parser.add_argument('-f', '--file_name', required=True, help='Filename')
parser.add_argument('-o', '--out_file', required=True, help='Output xls filename')
parser.add_argument('-i', '--input_file', required=True, help='Output xls filename')

args = parser.parse_args()
row_num = args.row_num
filename = args.file_name
out_file = args.out_file
input_file = args.input_file

_file = open(input_file, 'r')
one_conflict=''.join(_file.readlines())

if os.path.exists(out_file):
    rb = open_workbook(out_file, formatting_info=True)
    r_sheet = rb.sheet_by_index(0)   # read only copy to introspect the file
    wb = copy(rb)  # a writable copy (I can't read values out of this, only write to it)
    w_sheet = wb.get_sheet(0) # the sheet to write to within the writable copy
    w_sheet.write(int(row_num), 0, filename)
    w_sheet.write(int(row_num), 1, one_conflict)
    wb.save(out_file)

else:
    print "not exist"
    wbk = xlwt.Workbook(encoding='utf-8')

    w_sheet = wbk.add_sheet('conflicts')
    w_sheet.write(int(row_num), 0, filename)
    w_sheet.write(int(row_num), 1, one_conflict)
    wbk.save(out_file)
