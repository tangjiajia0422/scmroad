#!/bin/bash

if [ $1 = 'apply' ]; then
  ./main_apply.py
elif [ $1 = 'gen' ]; then
  ./main_gen.py
elif [ $1 = 'clean' ]; then
  ./main_clean.py
else
  echo "Sub command not supported."
fi
