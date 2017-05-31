#!/bin/bash

#===========================================
# 2015.11.02 Init
# 2015.11.03 Add print_result
# 2015.11.03 Enhancement for both author and committer
# 2015.11.04 Enhancement for no-merges/merges and better formmat for patch name
# 
# usage:
#      -e email, can use pattern match
#      -a grep author email
#      -c grep committer email
#      -m also include merged commits(parent 1)
#
#      $0 -e 'tang_jiajia@163.com' -a -c --> get all patches that committer/author is 'tang_jiajia@163.com'
#      $0 -e 'google.com|jenkins-auto.com' -a -c --> pattern matches, pattern is for 'grep -E'
#      $0 -e 'tang_jiajia@163.com' -a --> only get the patches that author is 'tang_jiajia@163.com'
#
# Author by tang_jiajia@163.com
#===========================================

DEFAULT_EMAIL_SUFIX="google.com"
MISS_PATHS=()
NO_PATCH_PATHS=()
MY_FEET=()
PATCH_RESULT="PATCH_RESULTS"
GIT_LOG_FORMAT="%H %ae %ce %P"
GIT_LOG_PARAMTER=""
PATCH_FILE_DATE_COMPARE=".git/HEAD"

function main(){
  CURRENT_PATH=$(pwd)
  CURRENT_MANIFEST="${CURRENT_PATH}/.repo/manifest.xml"
  CURRENT_PATCH_RESULT="${CURRENT_PATH}/${PATCH_RESULT}"
  check_parameters
  get_commits
  print_result
}

function usage(){
  echo "Example: $0 -e 'tang_jiajia@163.com'"
  echo "Example: $0 -e 'google.com|jenkins-auto.com'"
  exit 1
}

function print_result(){
  echo "================= Result ===================="
  echo "All the patch files$(find ${CURRENT_PATCH_RESULT} -type f | wc | awk '{print $1}'):"
  find ${CURRENT_PATCH_RESULT} -type f
  echo "=============== These ${#MY_FEET[@]} repos has my commits =================="
  echo "${MY_FEET[@]}"
  echo "============== Not found ${#MISS_PATHS[@]} repos: path missing ================"
  echo "${MISS_PATHS[@]}"
  echo "============ Not found ${EMAIL} in following ${#NO_PATCH_PATHS[@]} repos ==========="
  echo "${NO_PATCH_PATHS[@]}"
}

function make_patches(){
  each_path="$1"
  line="$2"
  local ABS_PATCH_LOCATED="${CURRENT_PATCH_RESULT}/${each_path}"
  mkdir -p "${ABS_PATCH_LOCATED}" || print_error "Can not mkdir ${ABS_PATCH_LOCATED}"
  commit_id=$(echo "${line}" | awk '{print $1}')
  parent_id=$(echo "${line}" | awk '{print $4}')
  if [ -n "${parent_id}" ]; then
    git format-patch "${commit_id}"^.."${commit_id}"
    o_patch_file=$(basename $(find . -maxdepth 1 -newer "${PATCH_FILE_DATE_COMPARE}" -name "*.patch"))
    t_patch_file_name=$(echo ${o_patch_file} | sed "s/^[0-9]\+/${commit_id}/g")
    mv "${o_patch_file}" "${ABS_PATCH_LOCATED}/${t_patch_file_name}"
  else
    git format-patch -1 "${commit_id}"
    o_patch_file=$(basename $(find . -maxdepth 1 -newer "${PATCH_FILE_DATE_COMPARE}" -name "*.patch"))
    t_patch_file_name=$(echo ${o_patch_file} | sed "s/^[0-9]\+/${commit_id}/g")
    mv "${o_patch_file}" "${ABS_PATCH_LOCATED}/${t_patch_file_name}"
  fi
}

function get_commits(){
  local i=0
  local j=0
  local k=0
  for each_path in $(get_repo_path "${CURRENT_MANIFEST}"); do
    local absolute_repo_path="${CURRENT_PATH}/${each_path}"
    cd "${absolute_repo_path}"
    if [ $? = 0 ]; then
      find_email=$(git log "${GIT_LOG_PARAMTER}" --format="${GIT_LOG_FORMAT}" | grep -E "${EMAIL}")
      if [ -n "${find_email}" ]; then
        sleep 2
        MY_FEET[i]="${each_path}"
        let i++
        # git log to print SHA-1, commiter-email, parent SHA-1
        git log "${GIT_LOG_PARAMTER}" --format="${GIT_LOG_FORMAT}" | while read line; do
          grep_author_result=$(echo "${line}" | awk '{print $2}' | grep -E "${EMAIL}")
          grep_committer_result=$(echo "${line}" | awk '{print $3}' | grep -E "${EMAIL}")
          grep_ac_result=$(echo "${line}" | awk '{print $2 $3}' | grep -E "${EMAIL}")
          if [ "${AUTHOR}" = "true" -a "${COMMITTER}" = "true" -a -n "${grep_ac_result}" ] || 
             [ "${AUTHOR}" = "false" -a "${COMMITTER}" = "false" -a -n "${grep_ac_result}" ]; then
            make_patches "${each_path}" "${line}"
            continue
          fi
          if [ "${AUTHOR}" = "true" ] && [ -n "${grep_author_result}" ]; then
            make_patches "${each_path}" "${line}"
            continue
          fi
          if [ "${COMMITTER}" = "true" ] && [ -n "${grep_committer_result}" ]; then
            make_patches "${each_path}" "${line}"
            continue
          fi
        done
      else
        NO_PATCH_PATHS[k]="${each_path}"
        let k++
      fi
    else
      print_error "Can not cd ${absolute_repo_path}"
      MISS_PATHS[j]="${each_path}"
      let j++
    fi
  done
}

function print_error(){
  echo -e "\e[1;31mError:$1\e[0m"
}

function print_ok(){
  echo -e "\e[1;32mOk:$1\e[0m"
}

function check_parameters(){
  if [ ! -f "${CURRENT_MANIFEST}" ]; then
    print_error "Could not find ${CURRENT_MANIFEST}, should be in a workspace."
  fi
  EMAIL=${EMAIL:-${DEFAULT_EMAIL_SUFIX}}
  AUTHOR="${AUTHOR:-false}"
  COMMITTER="${COMMITTER:-false}"
  if [ "${MERGE}" = "true" ]; then
    GIT_LOG_PARAMTER="-m --first-parent"
  else
    GIT_LOG_PARAMTER="--no-merges"
  fi
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

while getopts 'e:acm' OPTION; do
  case $OPTION in
       e)  #--Branch name
           EMAIL=$OPTARG
           echo "$0 EMAIL=${EMAIL}"
           ;;
       a)  #--By author
           AUTHOR="true"
           ;;
       c)  #--By committer
           COMMITTER="true"
           ;;
       m)  #--no-merge
           MERGE="true"
           ;;
       ?)  usage
           exit 2
           ;;
  esac
done

main
