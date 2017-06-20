#!/bin/bash

#
# SRC_WORKSPACE 是一个整的.git目录
# TARGET_WORKSPACE 是一个repo拆分好的目录
# 从SRC_WORKSPACE 迁移到TARGET_WORKSPACE 下的各个repo
#

#SRC 目录是一个整个git管理的目录
SRC_WORKSPACE="/home/help/tangjiajia/android4.4.3_d531"
#TARGET 目录是一个已经建好repo和分支的目标仓库
TARGET_WORKSPACE="/home/help/tangjiajia/pre-commit/new_verify"

#不是default.xml的主要原因是有git目录层级嵌套问题
DEFAULT_MANIFEST="${TARGET_WORKSPACE}/.repo/manifests/default_.xml"

#SRC_WORKSPACE="/home/help/tangjiajia/svn2git/apps"
#TARGET_WORKSPACE="/home/help/tangjiajia/pre-commit/new_verify/packages/apps/Hsae_Apps"
cd ${SRC_WORKSPACE}
#for each_path in $(ls)
for each_path in $(grep '<project' ${DEFAULT_MANIFEST} | sed 's/.*path=\"\([^\"]\+\)\".*/\1/g')
do
    cd ${SRC_WORKSPACE}
    #git checkout -f remotes/git-svn
    git checkout -f remotes/origin/merage
    _tmp=$(git log --no-merges --format="%H" "${each_path}" | tac)
    if [[ -z "${_tmp}" ]]; then
        continue
    fi
    #for each_sha1 in $(git log --no-merges --format="%H" "${each_path}" | tac)
    for each_sha1 in $(git log --no-merges --format="%H" "${each_path}" | tac | sed 1d)
    do
        cd ${SRC_WORKSPACE}
        git checkout -f "${each_sha1}"
        echo "Migrating ${each_sha1} for project: ${each_path}..."
        _subject=""
        _subject=$(git log "${each_sha1}" --format="%s" -1)
        if [[ -z "${_subject}" ]]; then
            _subject="Migrate from SVN"
        fi
        git log --name-status ${each_sha1} -1 --oneline | sed 1d | grep -v '^D' | awk '{$1=""; print $0}' | while read _each_file
        do
            _file_path=$(dirname "${_each_file}")
            mkdir -p "${TARGET_WORKSPACE}/${_file_path}"
            cp -frd "${SRC_WORKSPACE}/${_each_file}" "${TARGET_WORKSPACE}/${_each_file}"
        done
        git log --name-status ${each_sha1} -1 --oneline | sed 1d | grep '^D' | awk '{$1=""; print $0}' | while read _each_d_file
        do
            rm -rf "${TARGET_WORKSPACE}/${_each_d_file}"
        done
        cd "${TARGET_WORKSPACE}/${each_path}"; git add -A -f; git commit -m "${_subject}"
    done
done
