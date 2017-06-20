#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import os, sys
from utils import utils
from src_patches import src_patches
from version_check import version_check

script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]

version_check(script_path).check_all_versions()

a = utils(script_path).cfg_parser()
utils(script_path).print_defined_env(a)

gen_patches = src_patches(script_path).get_src_patches()
