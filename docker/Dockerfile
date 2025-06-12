FROM ghcr.io/linuxserver/baseimage-alpine:edge

###############################################################################
# YTDL-SUB INSTALL

# For phantomjs
ENV OPENSSL_CONF="/etc/ssl"
# For downloading thumbnails
ENV SSL_CERT_DIR="/etc/ssl/certs/"

COPY root/ /
RUN mkdir -p /config && \
    apk update --no-cache && \
    apk upgrade --no-cache && \
    apk add --no-cache --repository=http://dl-3.alpinelinux.org/alpine/edge/main/ \
      vim \
      g++ \
      nano \
      make \
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
    # Install phantomjs if using x86_64, ensure it is properly installed
    if [[ $(uname -m) == "x86_64" ]]; then \
      echo "installing phantomjs" && \
      apk add --no-cache gcompat && \
      cd /defaults && \
      tar -xj phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
      mv /defaults/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/share/phantomjs && \
      rm -rf /defaults/phantomjs-2.1.1-linux-x86_64 && \
      rm phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
      ln -s /usr/share/phantomjs /usr/bin/phantomjs && \
      echo "Phantom JS version:" && \
      phantomjs --version && \
      cd -; \
    fi && \
    echo "hi" && \
    # Install ytdl-sub, ensure it is installed properly
    python3 -m pip install --break-system-packages --no-cache-dir ytdl_sub-*.whl && \
      ytdl-sub -h && \
    # Delete unneeded packages after install
    rm ytdl_sub-*.whl && \
    apk del \
      g++ \
      make \
      libffi-dev \
      py3-pip \
      py3-setuptools

###############################################################################
# CONTAINER CONFIGS

ENV EDITOR="nano" \
HOME="/config" \
DOCKER_MODS=linuxserver/mods:universal-stdout-logs|linuxserver/mods:universal-cron \
DEFAULT_WORKSPACE=/config \
CRON_SCRIPT="/config/cron" \
CRON_WRAPPER_SCRIPT="/config/.cron_wrapper" \
LOGS_TO_STDOUT=/config/.cron.log \
LSIO_FIRST_PARTY=false

VOLUME /config