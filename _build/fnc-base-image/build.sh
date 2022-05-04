#!/bin/bash
ROOT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PARENT_DIR=`dirname $ROOT_DIR`

cd $ROOT_DIR

source "${PARENT_DIR}/.env"
DOCKERFILE="${ROOT_DIR}/Dockerfile"

docker build . \
    -t ${PROJECT_NAME}-fnc-base \
    -f ${DOCKERFILE}