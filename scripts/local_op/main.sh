#!/bin/bash

source my_color

help(){
  echo "1st step: 执行如下命令，生成所需要的patch..."
  echo "$0 gen"
  echo
  echo "2nd step: 执行如下命令，将生成的patch apply到目标项目..."
  echo "$0 apply"
  echo
  echo "Option step: 执行如下命令，恢复上下文..."
  echo "$0 clean"
}

if [ $1 = 'apply' ]; then
  ./main_apply.py
elif [ $1 = 'gen' ]; then
  ./main_gen.py
elif [ $1 = 'clean' ]; then
  ./main_clean.py
else
  echo "命令使用有错误，不支持子命令: $1 !" | _color_ red bold
  help
fi
