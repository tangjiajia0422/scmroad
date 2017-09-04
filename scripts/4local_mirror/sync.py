#!/usr/bin/python
# _*_ coding=utf-8 _*_

from manifest import ManifestParser as MP

def gen_clone_cmd():
    mp = MP('/home/mi/workspace/mi-codes/Gemini-MSM8996/A1-Gemini-M/.repo/manifest.xml')
    print mp.get_clone_list()

if __name__ == '__main__':
    gen_clone_cmd()

