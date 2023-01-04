FROM ghcr.io/linuxserver/baseimage-alpine:3.16

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      vim \
      g++ \
      nano \
      make \
      python3=~3.10 \
      py3-pip \
      py3-setuptools && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/community/ ffmpeg && \
    mkdir -p /config && \
    # Ensure ffmpeg is installed property
    ffmpeg -version && \
    # Install ytdl-sub, ensure it is installed propertly
    pip install --no-cache-dir ytdl_sub-*.whl && \
    ytdl-sub -h && \
    # Delete unneeded packages after install
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make \
      py3-setuptools

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config




