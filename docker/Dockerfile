FROM python:3.10.4-alpine3.15

###############################################################################
# S6 OVERLAY

ARG S6_OVERLAY_VERSION=3.1.0.1

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

###############################################################################
# YTDL-SUB INSTALL

COPY root/ /
RUN apk update && apk add \
    gcc \
    g++ \
    make \
    libffi-dev \
    openssl-dev \
    vim \
    bash \
    shadow && \
    echo "**** create abc user and make our folders ****" && \
    groupmod -g 1000 users && \
    useradd -u 911 -U -d /config -s /bin/false abc && \
    usermod -G users abc && \
    mkdir -p /config && \
    pip install ytdl_sub-*.whl

###############################################################################
# CONTAINER CONFIGS

# Environment Variables
ENV EDITOR="nano"   \
HOME="/config"



USER ${PUID}:${PGID}
VOLUME /config

ENTRYPOINT ["/init"]




