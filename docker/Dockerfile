FROM ghcr.io/linuxserver/baseimage-alpine:3.15

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN apk update && \
    apk add \
      vim \
      gcc \
      g++ \
      make \
      libffi-dev \
      openssl-dev && \
    apk del \
      python3 \
      py3-pip && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      python3=3.10.4-r0 \
      py3-setuptools=59.4.0-r0 && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/community/ \
      py3-pip=22.0.4-r0 && \
    mkdir -p /config && \
    pip install --no-cache-dir ytdl_sub-*.whl && \
    rm ytdl_sub-*.whl

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config




