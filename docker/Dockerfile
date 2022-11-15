FROM ghcr.io/linuxserver/baseimage-alpine:3.15

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN apk update --no-cache && \
    apk add \
      vim \
      g++ \
      nano \
      make && \
    # Install yt-dlp patched ffmpeg
    if [ `uname -m` = "x86_64" ]; then \
      wget "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz" -O ffmpeg.tar.xz; \
    else \
      wget "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz" -O ffmpeg.tar.xz; \
    fi && \
    mkdir ffmpeg_out && \
    tar -xf ffmpeg.tar.xz -C ffmpeg_out/ --strip-components 1 && \
    mv ffmpeg_out/bin/* /usr/local/bin/ && \
    rm -rf ffmpeg.tar.xz ffmpeg_out/ && \
    apk del \
      python3 \
      py3-pip && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      python3=~3.10 \
      py3-setuptools && \
    apk add --repository=http://dl-3.alpinelinux.org/alpine/edge/community/ \
      py3-pip && \
    mkdir -p /config && \
    pip install --no-cache-dir ytdl_sub-*.whl && \
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make \
      py3-setuptools

RUN ls -lh /usr/local/bin | grep ff && \
    ffmpeg -version && \
    ffprobe -version

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config"

VOLUME /config




