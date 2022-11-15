FROM ghcr.io/linuxserver/baseimage-alpine:3.16

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN apk update --no-cache && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      vim \
      g++ \
      nano \
      make \
      python3=~3.10 \
      py3-setuptools && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/community/ \
      ffmpeg \
      py3-pip && \
    mkdir -p /config && \
    pip install --no-cache-dir ytdl_sub-*.whl && \
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make \
      py3-setuptools \
      py3-pip

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config




