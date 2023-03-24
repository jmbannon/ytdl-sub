FROM ghcr.io/linuxserver/baseimage-alpine:edge

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN mkdir -p /config && \
    apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      vim \
      g++ \
      nano \
      make \
      "python3>=3.10" \
      py3-pip \
      fontconfig \
      py3-setuptools && \
    # Install edge ffmpeg, ensure it is properly installed
    apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
      "ffmpeg>5.1" && \
      ffmpeg -version && \
    # Install phantomjs if using x86_64, ensure it is properly installed
    if [[ $(uname -m) == "x86_64" ]]; then \
      cd /usr/share && \
      curl -L https://github.com/Overbryd/docker-phantomjs-alpine/releases/download/2.11/phantomjs-alpine-x86_64.tar.bz2 | tar xj && \
      ln -s /usr/share/phantomjs/phantomjs /usr/bin/phantomjs && \
      echo "Phantom JS version:" && \
      phantomjs --version && \
      cd -; \
    fi && \
    # Install ytdl-sub, ensure it is installed properly
    python3 -m pip install --no-cache-dir ytdl_sub-*.whl && \
      ytdl-sub -h && \
    # Delete unneeded packages after install
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make \
      py3-pip \
      py3-setuptools

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config