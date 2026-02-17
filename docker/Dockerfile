FROM ghcr.io/linuxserver/baseimage-alpine:edge

###############################################################################
# YTDL-SUB INSTALL

# For phantomjs
ENV OPENSSL_CONF="/etc/ssl"
# For downloading thumbnails
ENV SSL_CERT_DIR="/etc/ssl/certs/"
# Working directory used at both build and run times:
ENV DEFAULT_WORKSPACE="/config"

COPY root/ /
RUN mkdir -pv "${DEFAULT_WORKSPACE}" && \
    apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      vim \
      g++ \
      nano \
      unzip \
      make \
      deno \
      libffi-dev \
      "python3>=3.10" \
      py3-pip \
      fontconfig \
      py3-setuptools && \
    # Install edge ffmpeg and aria2 from community, ensure they are properly installed
    apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
      "ffmpeg>5.1" \
      "aria2>=1.36.0" && \
    ffmpeg -version && \
    aria2c --version && \
    deno --version && \
    # Install phantomjs if using x86_64, ensure it is properly installed
    if [[ $(uname -m) == "x86_64" ]]; then \
      echo "installing phantomjs" && \
      apk add --no-cache gcompat && \
      tar -xjvf /defaults/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
      mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/share/phantomjs && \
      rm -rf phantomjs-2.1.1-linux-x86_64 && \
      rm /defaults/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
      ln -s /usr/share/phantomjs /usr/bin/phantomjs && \
      echo "Phantom JS version:" && \
      phantomjs --version && \
      cd -; \
    fi && \
    # Configure pip globally
    echo -e "[global]\nbreak-system-packages = true\nroot-user-action = ignore\nno-cache-dir = true" > /etc/pip.conf && \
    # Install ytdl-sub and yt-dlp dependencies, ensure they are installed properly
    python3 -m pip install ytdl_sub-*.whl curl-cffi yt-dlp-ejs && \
      ytdl-sub -h && \
    # Delete unneeded packages after install
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make \
      libffi-dev && \
    python3 -m pip --help


###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="${DEFAULT_WORKSPACE}" \
DOCKER_MODS=linuxserver/mods:universal-stdout-logs|linuxserver/mods:universal-cron \
CRON_SCRIPT="${DEFAULT_WORKSPACE}/cron" \
CRON_WRAPPER_SCRIPT="${DEFAULT_WORKSPACE}/.cron_wrapper" \
LOGS_TO_STDOUT="${DEFAULT_WORKSPACE}/.cron.log" \
LSIO_FIRST_PARTY=false

VOLUME "${DEFAULT_WORKSPACE}"
WORKDIR "${DEFAULT_WORKSPACE}"
