FROM python:3.9-slim

ARG GCF_TARGET "fnc_target"
ARG GCF_SIGNATURE_TYPE "event"

ENV GCF_TARGET=$GCF_TARGET
ENV GCF_SIGNATURE_TYPE=$GCF_SIGNATURE_TYPE

COPY . .

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
RUN pip install functions-framework

CMD functions-framework --target ${GCF_TARGET} --signature-type ${GCF_SIGNATURE_TYPE}
