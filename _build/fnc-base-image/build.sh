#!/bin/bash
SELF=`readlink -f $0`
ROOT_DIR=`dirname $SELF`
PARENT_DIR=`dirname $(dirname $SELF)`

cd $ROOT_DIR

source "${PARENT_DIR}/.env"
DOCKERFILE="${ROOT_DIR}/Dockerfile"

docker build . \
    -t ${PROJECT_NAME}-fnc-base \
    -f ${DOCKERFILE}