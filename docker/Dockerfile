FROM ghcr.io/linuxserver/baseimage-ubuntu:jammy

# https://askubuntu.com/questions/972516/debian-frontend-environment-variable
ARG DEBIAN_FRONTEND=noninteractive

# https://github.com/NVIDIA/nvidia-docker/wiki/Installation-(Native-GPU-Support)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES="compute,video,utility"

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN mkdir -p /config && \
    apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install --no-install-recommends -y \
      software-properties-common && \
    add-apt-repository ppa:savoury1/ffmpeg4 && \
    add-apt-repository ppa:savoury1/ffmpeg5 && \
    apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install --no-install-recommends -y \
      vim \
      g++ \
      nano \
      make \
      python3.10-dev \
      python3-pip \
      fontconfig \
      python3-venv \
    # Ensure ffmpeg is properly installed
      ffmpeg && \
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
    pip install --no-cache-dir ytdl_sub-*.whl && \
      ytdl-sub -h && \
      ldconfig && \
    # Delete unneeded packages after install
    rm ytdl_sub-*.whl && \
    apt-get remove -y \
      g++ \
      make \
      python3.10-dev \
      python3-venv && \
    apt-get autoremove -y && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config