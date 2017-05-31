#!/bin/bash

#===========================================
# $0 -p 'quicl' -l 'http://172.16.11.162:8081' -u 'tang_jiajia' -n '242982'
#===========================================

CURRENT_PWD=$(pwd)
DEFAULT_MANIFEST="${CURRENT_PWD}/.repo/manifest.xml"

function main(){
  get_gerrit_info
  do_cherrypick
}

function print_error(){
  echo -e "\e[1;31mError:$1\e[0m"
}

function print_ok(){
  echo -e "\e[1;32mOk:$1\e[0m"
}

function do_cherrypick(){
  CHERRY_PICKED_IDS=()
  DUPLICATED_IDS=()
  local i=0
  local j=0
  for each_id in $(echo "${CHERRY_PICK_LIST}"); do
    local GERRIT_ID="${each_id}"
    if [[ "${each_id}" =~ ^[0-9]+,[1-9]+ ]]; then
      local GERRIT_ID=$(echo "${each_id}" | awk -F ',' '{print $1}')
      local GEVEN_PATCH_SET=$(echo "${each_id}" | awk -F ',' '{print $2}')
    fi
    # Need to check if given cherry-pick list has duplicate ids
    if_cherry_picked_ids_contains "${CHERRY_PICKED_IDS}" "${GERRIT_ID}"
    if [ $? = 0 ]; then
      CHERRY_PICKED_IDS[i]="${GERRIT_ID}"
      let i++
    else
      DUPLICATED_IDS[j]="${GERRIT_ID}"
      let j++
    fi
    if [ "${#DUPLICATED_IDS[@]}" != "0" ]; then
      print_error "duplicated IDs: ${DUPLICATED_IDS[@]}"
      exit 0
    fi
  done
  for each_needed_id in $(echo "${CHERRY_PICK_LIST}"); do
    local NEEDED_GERRIT_ID="${each_needed_id}"
    if [[ "${each_needed_id}" =~ ^[0-9]+,[1-9]+ ]]; then
      local NEEDED_GERRIT_ID=$(echo "${each_needed_id}" | awk -F ',' '{print $1}')
      local NEEDED_PATCH_SET=$(echo "${each_needed_id}" | awk -F ',' '{print $2}')
    fi
    # end of check duplicate ids
    parser_cherry_pick_list "${NEEDED_GERRIT_ID}" "${NEEDED_PATCH_SET}"
  done
}

function if_cherry_picked_ids_contains(){
  local array_list=$1
  local to_check_id=$2
  for already_id in $(echo ${array_list[@]}); do
  #local to_check_id=$1
  #for already_id in $(echo ${CHERRY_PICKED_IDS[@]}); do
    if [ "${already_id}" = "${to_check_id}" ]; then
      return 1
    fi
  done
  return 0
}

function get_gerrit_info(){
  if [ -z "${GERRIT_URL}" ]; then
    usage
  fi
  local info_result=$(wget --no-check-certificate -q -O - "${GERRIT_URL}/ssh_info")
  # info_result should be like: "192.168.65.161 29418", make sure this
  if [[ "${info_result}" =~ ^([0-9]{1,3}.){3}[0-9]{1,3}\d*[0-9]+ ]]; then
    GERRIT_HOST=$(echo ${info_result} | awk '{print $1}')
    GERRIT_PORT=$(echo ${info_result} | awk '{print $2}')
  fi
  if [ -z "${GERRIT_HOST}" -o -z "${GERRIT_PORT}" ]; then
    print_error "count not get ip and ssh port by given ${GERRIT_URL}"
    exit 1
  fi
}

function parser_cherry_pick_list(){
  local GERRIT_ID=$1
  local GEVEN_PATCH_SET=$2
  local query_result=$(ssh -p "${GERRIT_PORT}" "${GERRIT_USER}"@"${GERRIT_HOST}" gerrit query --format=JSON --commit-message "${GERRIT_ID}" --current-patch-set | sed '2d' | python -c 'import json,sys;reload(sys);sys.setdefaultencoding("utf-8");json_str=json.loads(sys.stdin.readline());project_name = json_str["project"]; patchset_parents = json_str["currentPatchSet"]["parents"]; parents = len(patchset_parents); patchset = json_str["currentPatchSet"]["number"]; patch_ref = json_str["currentPatchSet"]["ref"];print "%s|%s|%s|%s" %(project_name, patchset, patch_ref, parents)')
  if [[ "${query_result}" =~ \S*|\S+|\S+ ]]; then
    local PATCH_PROJECT=$(echo "${query_result}" | awk -F '|' '{print $1}')
    local PATCH_SET=$(echo "${query_result}" | awk -F '|' '{print $2}')
    local PATCH_REF=$(echo "${query_result}" | awk -F '|' '{print $3}')
    local PATCH_PARENTS=$(echo "${query_result}" | awk -F '|' '{print $4}')
  else
    print_error "query ${GERRIT_ID} failed:"
    print_error "please eval command local--> ssh -p ${GERRIT_PORT} ${GERRIT_USER}@${GERRIT_HOST} gerrit query --format=JSON --commit-message ${GERRIT_ID} --current-patch-set | sed '2d'"
    exit 1
  fi
  if [ -n "${GEVEN_PATCH_SET}" ]; then
    PATCH_SET="${GEVEN_PATCH_SET}"
    PATCH_REF="${PATCH_REF%/*}/${PATCH_SET}"
  fi
  local project_path=$(get_path_by_project_name "${PATCH_PROJECT}")
  if [ -n "${project_path}" -a -e "${CURRENT_PWD}/${project_path}" ]; then
    if [ "${PATCH_PARENTS}" != "1" ]; then
       echo "${PATCH_REF} is a merge commit, default is 'git cherry-pick -m 1 FETCH_HEAD'"
       echo "cd "${CURRENT_PWD}/${project_path}"; git fetch ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/${PATCH_PROJECT} ${PATCH_REF} && git cherry-pick -m 1 FETCH_HEAD"
       cd "${CURRENT_PWD}/${project_path}"
       git fetch ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/${PATCH_PROJECT} ${PATCH_REF} && git cherry-pick -m 1 FETCH_HEAD
    else
       echo "cd "${CURRENT_PWD}/${project_path}"; git fetch ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/${PATCH_PROJECT} ${PATCH_REF} && git cherry-pick FETCH_HEAD"
       cd "${CURRENT_PWD}/${project_path}"
       git fetch ssh://${GERRIT_USER}@${GERRIT_HOST}:${GERRIT_PORT}/${PATCH_PROJECT} ${PATCH_REF} && git cherry-pick FETCH_HEAD
    fi
    if [ $? != "0" -o -e ".git/MERGE_MSG" ]; then
      print_error "cherry-pick ${GERRIT_ID} failed, due to conflicts!"
      exit 1
    fi
  else
    print_error "${PATCH_PROJECT}<->${project_path} does not exit"
    exit 1
  fi
}

function get_path_by_project_name(){
  local project_name=$1
  if [ -e "${DEFAULT_MANIFEST}" ]; then
    local real_project_name=$(echo "${project_name}" | awk -F "${PROJECT_PREFIX}/" '{print $2}')
    local real_path=$(grep "name=[\"]${real_project_name}[\"]" "${DEFAULT_MANIFEST}" | sed 's/.*path=\"\([^\"]*\)\".*/\1/' | sed 's/.*name=\"\([^\"]*\)\".*/\1/')
    echo "${real_path}"
  else
    print_error "could not find ${DEFAULT_MANIFEST}"
    exit 1
  fi
}

function usage(){
  echo "$0 -p '<PROJECT_PREFIX>' -l '<GERRIT_URL>' -u '<GERRIT_USER>' -n '<CHERRY_PICK_LIST>'"
  echo "Example: $0 -p 'quicl' -l 'http://192.168.65.24:8000' -u 'tang_jiajia' -n '90123 90245 10002,1'"
  exit 1
}

while getopts 'p:b:l:u:n:' OPTION; do
  case $OPTION in
       p)  #--Project prefix
           PROJECT_PREFIX=$OPTARG
           echo "$0 PROJECT_PREFIX=${PROJECT_PREFIX}"
           ;;
       l)  #--Gerrit url:http://172.16.11.162:8081/
           GERRIT_URL=$OPTARG
           echo "$0 GERRIT_URL=${GERRIT_URL}"
           ;;
       u)  #--Gerrit username
           GERRIT_USER=$OPTARG
           echo "$0 GERRIT_USER=${GERRIT_USER}"
           ;;
       n)  #--Cherry-pick list
           CHERRY_PICK_LIST=$OPTARG
           echo "$0 CHERRY_PICK_LIST=${CHERRY_PICK_LIST}"
           ;;
       ?)  usage
           exit 2
           ;;
  esac
done

main
