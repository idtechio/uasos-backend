ARG PROJECT_NAME
FROM $PROJECT_NAME-fnc-base

ARG GCF_TARGET "fnc_target"
ARG GCF_SIGNATURE_TYPE "event"

ENV GCF_TARGET=${GCF_TARGET}
ENV GCF_SIGNATURE_TYPE=${GCF_SIGNATURE_TYPE}

COPY . .

RUN pip install -r ./requirements.txt

CMD functions-framework --target ${GCF_TARGET} --signature-type ${GCF_SIGNATURE_TYPE}
