FROM ghcr.io/linuxserver/baseimage-alpine:3.15

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN apk update --no-cache && \
    apk add \
      vim \
      g++ \
      make \
      ffmpeg && \
    apk del \
      python3 \
      py3-pip && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      python3=3.10.4-r0 \
      py3-setuptools=59.4.0-r0 && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/community/ \
      py3-pip && \
    mkdir -p /config && \
    pip install --no-cache-dir ytdl_sub-*.whl && \
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config




