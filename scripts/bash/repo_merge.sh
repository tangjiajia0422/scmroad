#!/bin/bash

#===========================================
# 2015.10.27 Init
# 2015.10.28 Add usage and control_c for trap signal
# 2015.10.29 Optimized and more logical
# 2015.11.23 Print better result
#
# Author by tang_jiajia@163.com
# usage:
#       $0 -b branch_name
#       $0 -t tag_name
#       $0 -m static_manifest.xml
# Only one parameter(-b OR -t OR -m) needed! 
# It depends on which you want to be merged, branch or tag or static_manifest.xml?
#===========================================

CURRENT_REPO_PATHS=()
CURRENT_REPO_REMOTE=""
STATIC_REPO_PATHS=()
REAL_NEED_MERGE_REPO_PATHS=()
MERGED_REPO_PATHS=()
ERRORED_MERGE_PATH=()
NEED_MERGE_MANNUALLY=()
NOT_MERGE_PATH=()
MERGE_PATH_MISS=()
REPO_PATHS_MORE_THAN_STATIC=()
STATIC_PATHS_MORE_THAN_REPO=()
CURRENT_PWD=$(pwd)

function main(){
  CURRENT_MANIFEST="${CURRENT_PWD}/.repo/manifest.xml"
  MANIFEST_REPO="${CURRENT_PWD}/.repo/manifests"
  CURRENT_REPO_REMOTE_DEFAULT=$(cat "${CURRENT_MANIFEST}" | python -c 'from xml.etree import ElementTree as ET; import sys;tree = ET.parse(sys.stdin);root = tree.getroot();remote_elem = root.iter("remote").next();remote_name = remote_elem.get("name");print remote_name')
  assign_c_path
  check_parameters
  if [ -n "${STATIC_MANIFEST}" ]; then
    assign_s_path
    get_repo_paths_more_than_static
    get_static_paths_more_than_repo
  else
    REAL_NEED_MERGE_REPO_PATHS=$(echo "${CURRENT_REPO_PATHS[@]}")
  fi
  if [ -n "${BRANCH_NAME}" ] || [ -n "${TAG_NAME}" ]; then
    merge_manifest
  fi
  do_merge
  print_results
}

function usage(){
  echo "$0 -b branch_name --> Example: $0 -b 'local_branch'"
  echo "OR"
  echo "$0 -t tag_name --> Example: $0 -t 'local_tag'"
  echo "OR"
  echo "$0 -m static_manifest.xml --> Example: $0 -m 'static_manifest.xml'"
  exit 1
}

function control_c(){
  echo "\nCaught Control-C, listing current status!"
  echo "Already merged ${#MERGED_REPO_PATHS[@]}(total:${#CURRENT_REPO_PATHS[@]}): ${REAL_NEED_MERGE_REPO_PATHS[@]}"
  exit 3
}

function check_parameters(){
  local j=0
  if [ ! -f "${CURRENT_MANIFEST}" ]; then
    print_error "Could not find ${CURRENT_MANIFEST}, should be in a workspace."
  fi

  if [ -n "${BRANCH_NAME}" ]; then
    let j++
  fi
  if [ -n "${TAG_NAME}" ]; then
    let j++
  fi
  if [ -n "${STATIC_MANIFEST}" ]; then
    let j++
  fi
  if [ $j -ne 1 ]; then
    print_error "More than one parameter!"
  fi
}

function print_error(){
  echo -e "\e[1;31mError:$1\e[0m"
}

function print_ok(){
  echo -e "\e[1;32mOk:$1\e[0m"
}

function print_results(){
  REAL_NEED_MERGE_REPO_PATHS_LENGTH="${#REAL_NEED_MERGE_REPO_PATHS[@]}"
  CURRENT_REPO_PATHS_LENGTH="${#CURRENT_REPO_PATHS[@]}"
  REPO_PATHS_MORE_THAN_STATIC_LENGTH="${#REPO_PATHS_MORE_THAN_STATIC[@]}"
  STATIC_PATHS_MORE_THAN_REPO_LENGTH="${#STATIC_PATHS_MORE_THAN_REPO[@]}"
  STATIC_REPO_PATHS_LENGTH="${#STATIC_REPO_PATHS[@]}"
  MERGED_REPO_PATHS_LENGTH="${#MERGED_REPO_PATHS[@]}"
  ERRORED_MERGE_PATH_LENGTH="${#ERRORED_MERGE_PATH[@]}"
  NOT_MERGE_PATH_LENGTH="${#NOT_MERGE_PATH[@]}"
  echo "=============== RESULTS =================="
  echo "The following ${REAL_NEED_MERGE_REPO_PATHS_LENGTH}(total:${CURRENT_REPO_PATHS_LENGTH}) repos will be exec merge operation"
  echo "${REAL_NEED_MERGE_REPO_PATHS[@]}"
  if [ ! "${REPO_PATHS_MORE_THAN_STATIC_LENGTH}" = "0" ]; then
    echo "=========================================="
    echo "Current ${CURRENT_MANIFEST}(${CURRENT_REPO_PATHS_LENGTH}-${REAL_NEED_MERGE_REPO_PATHS_LENGTH}) has (${REPO_PATHS_MORE_THAN_STATIC_LENGTH}) more repos than ${STATIC_MANIFEST}, NOT merge following repos:"
    echo "${REPO_PATHS_MORE_THAN_STATIC[@]}"
  fi
  if [ ! "${STATIC_PATHS_MORE_THAN_REPO_LENGTH}" = "0" ]; then
    echo "=========================================="
    echo "${STATIC_MANIFEST}(${STATIC_REPO_PATHS_LENGTH}-${REAL_NEED_MERGE_REPO_PATHS_LENGTH}) has (${STATIC_PATHS_MORE_THAN_REPO_LENGTH}) more repos than ${CURRENT_MANIFEST}, NOT merge following repos:"
    echo "${STATIC_PATHS_MORE_THAN_REPO[@]}"
  fi
  echo "=========================================="
  echo "Revision miss, not merge ${NOT_MERGE_PATH_LENGTH}(total:${CURRENT_REPO_PATHS_LENGTH}): ${NOT_MERGE_PATH[@]}"
  echo "=========================================="
  echo "Path miss, not merge ${#MERGE_PATH_MISS[@]}(total:${CURRENT_REPO_PATHS_LENGTH}): ${MERGE_PATH_MISS[@]}"
  echo "=========================================="
  echo "Already merged: ${MERGED_REPO_PATHS_LENGTH}(total:${CURRENT_REPO_PATHS_LENGTH})"
  echo "=========================================="
  echo "Merge errors: ${ERRORED_MERGE_PATH_LENGTH}(total:${CURRENT_REPO_PATHS_LENGTH}): ${ERRORED_MERGE_PATH[@]}"
  echo "=========================================="
  #echo "Please merge mannually or resolve conflicts: $(print_array ${NEED_MERGE_MANNUALLY})"
  echo "Please merge mannually or resolve conflicts: $(echo ${NEED_MERGE_MANNUALLY[@]} | tr '|' '\n')"
  echo "============== RESULTS DONE =============="
}

function get_repo_path(){
  declare -a repo_paths
  local j=0
  for i in $(grep "<project" $1 | sed 's/.*path=\"\([^\"]*\)\".*/\1/' | sed 's/.*name=\"\([^\"]*\)\".*/\1/'); do
    repo_paths[j]=${i}
    let j++
  done
  echo "${repo_paths[@]}"
}

function get_remote(){
  local repo_remote=$(grep -E "name=[\"]${1}[\"]|path=[\"]${1}[\"]" "${CURRENT_MANIFEST}" | grep "remote=\"" | sed 's/.*remote=\"\([^\"]*\)\".*/\1/')
  if [ -n "${repo_remote}" ]; then
    CURRENT_REPO_REMOTE="${repo_remote}"
  else
    CURRENT_REPO_REMOTE="${CURRENT_REPO_REMOTE_DEFAULT}"
  fi
  echo "${CURRENT_REPO_REMOTE}"
}

function assign_c_path(){
  local i=0
  for each_c_path in $(get_repo_path "${CURRENT_MANIFEST}"); do
    CURRENT_REPO_PATHS[i]="${each_c_path}"
    let i++
  done
}

function assign_s_path(){
  local i=0
  for each_s_path in $(get_repo_path "${STATIC_MANIFEST}"); do
    STATIC_REPO_PATHS[i]="${each_s_path}"
    let i++
  done
}

function get_repo_paths_more_than_static(){
  local i=0
  local j=0
  for each_repo_path in $(echo "${CURRENT_REPO_PATHS[@]}"); do
    grep_result=$(grep -E "name=[\"]${each_repo_path}[\"]|path=[\"]${each_repo_path}[\"]" "${STATIC_MANIFEST}")
    if [ -n "${grep_result}" ]; then
      REAL_NEED_MERGE_REPO_PATHS[i]="${each_repo_path}"
      let i++
    else
      REPO_PATHS_MORE_THAN_STATIC[j]="${each_repo_path}"
      let j++
    fi
    unset grep_result
  done
}

function get_static_paths_more_than_repo(){
  local j=0
  for each_repo_path_static in $(echo "${STATIC_REPO_PATHS[@]}"); do
    grep_result=$(grep -E "name=[\"]${each_repo_path_static}[\"]|path=[\"]${each_repo_path_static}[\"]" "${CURRENT_MANIFEST}")
    if [ -n "${grep_result}" ]; then
      :
    else
      STATIC_PATHS_MORE_THAN_REPO[j]="${each_repo_path_static}"
      let j++
    fi
    unset grep_result
  done
}

function merge_branch_tag(){
  local current_head=$1
  local each_path=$2
  local j=$3
  head_revision=$(git log "${current_head}" --format=%H -1)
  git merge "${head_revision}"
  if [ $? != 0 ]; then
    git merge --abord
    git clean -dfx
    error_message="Merge failed:${each_path} ==> git merge ${current_head} <<>> ${head_revision}"
    ERRORED_MERGE_PATH[j]="${each_path}"
    NEED_MERGE_MANNUALLY[j]="cd ${each_path}; git merge ${current_head} |"
    print_error "${error_message}"
  else
    MERGED_REPO_PATHS[j]="${each_path}"
    print_ok "Merge success:${each_path} ==> git merge ${current_head} <<>> ${head_revision}"
  fi
}

function merge_manifest(){
  # If branch or tag, need to merge manifest first. Incase add/remove any repos
  cd "${MANIFEST_REPO}" || print_error "Could not cd ${MANIFEST_REPO}"
  local manifest_remote=$(git remote -v | sed '2,$d' | awk '{print $1}')
  if [ -n "${BRANCH_NAME}" ]; then
    local log_remote_branch="${manifest_remote}/${BRANCH_NAME}"
    if git branch -a | grep -w -E "${log_remote_branch}$"; then
      merge_branch_tag "${log_remote_branch}" "${MANIFEST_REPO}" "0"
    else
      NOT_MERGE_PATH[0]="${MANIFEST_REPO}"
      print_error "Not found ${log_remote_branch} in ${MANIFEST_REPO}"
    fi
  fi
  if [ -n "${TAG_NAME}" ]; then
    if git tag -l | grep -w -E "${TAG_NAME}$"; then
      merge_branch_tag "${TAG_NAME}" "${MANIFEST_REPO}" "0"
    else
      NOT_MERGE_PATH[0]="${MANIFEST_REPO}"
      print_error "Not found ${TAG_NAME} in ${MANIFEST_REPO}"
    fi
  fi
  cd "${CURRENT_PWD}"
}

function do_merge(){
  local revision
  local j=0
  declare -a merged_repo_paths
  if [ -n "${STATIC_MANIFEST}" ]; then
    revision=$(grep "<default" "${STATIC_MANIFEST}" | sed 's/.*revision=\"\([^\"]*\)\".*/\1/')
  fi
  for each_path in $(echo "${REAL_NEED_MERGE_REPO_PATHS[@]}"); do
    let j++
    absolut_path=${CURRENT_PWD}/${each_path}
    cd "${absolut_path}"
    if [ $? != 0 ]; then
       MERGE_PATH_MISS[j]="${each_path}"
       print_error "Could not cd ${absolut_path}"
       continue
    fi
    if [ -n "${BRANCH_NAME}" ]; then
      local my_remote=$(get_remote "${each_path}")
      local log_remote_branch="${my_remote}/${BRANCH_NAME}"
      if git branch -a | grep -w -E "${log_remote_branch}$"; then
        merge_branch_tag "${log_remote_branch}" "${each_path}" "$j"
        continue
      else
        NOT_MERGE_PATH[j]="${each_path}"
        print_error "Not found ${log_remote_branch} in ${absolut_path}"
      fi
    fi
    if [ -n "${TAG_NAME}" ]; then
      if git tag -l | grep -w -E "${TAG_NAME}$"; then
        merge_branch_tag "${TAG_NAME}" "${each_path}" "$j"
        continue
      else
        NOT_MERGE_PATH[j]="${each_path}"
        print_error "Not found ${TAG_NAME} in ${absolut_path}"
      fi
    fi
    if [ -n "${STATIC_MANIFEST}" ]; then
      revision=$(grep "<project" "${STATIC_MANIFEST}" | grep -E "name=[\"]${each_path}[\"]|path=[\"]${each_path}[\"]" | sed 's/.*revision=\"\([^\"]*\)\".*/\1/')
      if [ -z "${revision}" ]; then
        print_error "Revision parser failed, null"
      else
        find_revision=$(git log --format=%H "${revision}" -1)
        find_branch_rev=$(git branch -a | grep -w -E "${revision}$")
        find_tag_rev=$(git tag -l | grep -w -E "${revision}$")
        if [ -z "${find_revision}" -a -z "${find_branch_rev}" -a -z "${find_tag_rev}" ]; then
          NOT_MERGE_PATH[j]="${each_path}"
          print_error "Could not find ${revision} in ${each_path}"
        else
          merge_branch_tag "${revision}" "${each_path}" "$j"
          continue
        fi
      fi
    fi
  done
}

while getopts 'b:t:m:' OPTION; do
  case $OPTION in
       b)  #--Branch name
           BRANCH_NAME=$OPTARG
           echo "$0 BRANCH_NAME=${BRANCH_NAME}"
           ;;
       t)  #--Tag name
           TAG_NAME=$OPTARG
           echo "$0 TAG_NAME=${TAG_NAME}"
           ;;
       m)  #--Static manifest file
           STATIC_MANIFEST=$OPTARG
           echo "$0 STATIC_MANIFEST=${STATIC_MANIFEST}"
           ;;
       ?)  usage
           exit 2
           ;;
  esac
done

trap control_c SIGINT
main
