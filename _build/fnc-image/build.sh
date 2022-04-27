#!/bin/bash
SELF=`readlink -f $0`
ROOT_DIR=`dirname $SELF`
PARENT_DIR=`dirname $(dirname $SELF)`

cd $ROOT_DIR

source "${PARENT_DIR}/.env"
DOCKERFILE="${ROOT_DIR}/Dockerfile"

FNC_DIR="${PARENT_DIR}/../${GCF_DIR}/${GCF_NAME}"

if [ ! -d "${FNC_DIR}" ]
then
    echo "Function directory DOES NOT exists." 
    exit 999
fi

# read GCF_SIGNATURE_TYPE, GCF_TARGET, GCF_RUNTIME
if [ -f "${FNC_DIR}/.env_buildpack" ]
then
    source "${FNC_DIR}/.env_buildpack"
else
    source "./.env_buildpack"
fi

cd "${FNC_DIR}"

GCF_IMAGE_NAME="${PROJECT_NAME}-fnc-${GCF_NAME}"

if [[ "$BUILDER" = "custom" ]]
then
    docker build . \
        --no-cache \
        -t ${GCF_IMAGE_NAME} \
        -f ${DOCKERFILE} \
        --build-arg PROJECT_NAME=${PROJECT_NAME} \
        --build-arg GCF_SIGNATURE_TYPE=${GCF_SIGNATURE_TYPE} \
        --build-arg GCF_TARGET=${GCF_TARGET}
fi

if [[ "$BUILDER" = "pack" ]]
then
    pack build \
        --builder gcr.io/buildpacks/builder:latest \
        --env GOOGLE_FUNCTION_SIGNATURE_TYPE="${GCF_SIGNATURE_TYPE}" \
        --env GOOGLE_FUNCTION_TARGET="${GCF_TARGET}" \
        --env GOOGLE_RUNTIME="${GCF_RUNTIME}" \
        "${GCF_IMAGE_NAME}"
fi