FROM ghcr.io/linuxserver/baseimage-alpine:3.17

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
      python3=~3.10 \
      py3-pip \
      fontconfig \
      py3-setuptools && \
    # Install ffmpeg, ensure it is properly installed
    if [[ $(uname -m) == "x86_64" ]]; then \
      curl -L -o ffmpeg.tar.gz https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz && \
      tar -xf ffmpeg.tar.gz && \
      chmod +x ffmpeg-master-latest-linux64-gpl/bin/ffmpeg && \
      chmod +x ffmpeg-master-latest-linux64-gpl/bin/ffprobe && \
      mv ffmpeg-master-latest-linux64-gpl/bin/ffmpeg /usr/bin/ffmpeg && \
      mv ffmpeg-master-latest-linux64-gpl/bin/ffprobe /usr/bin/ffprobe && \
      ls -lh /usr/bin && \
      rm ffmpeg.tar.gz && \
      rm -rf ffmpeg-master-latest-linux64-gpl/ ; \
    else \
      curl -L -o ffmpeg.tar.gz https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz && \
      tar -xf ffmpeg.tar.gz && \
      chmod +x ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg && \
      chmod +x ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe && \
      mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg /usr/bin/ffmpeg && \
      mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe /usr/bin/ffprobe && \
      rm ffmpeg.tar.gz && \
      rm -rf ffmpeg-master-latest-linuxarm64-gpl/ ; \
    fi && \
    # Ensure ffmpeg is installed
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