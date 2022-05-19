FROM python:3.10.4-alpine3.15

# Needed for py deps
RUN apk add gcc g++ make libffi-dev openssl-dev

USER ${PUID}:${PGID}
COPY ytdl_sub-0.0.1-py3-none-any.whl .

RUN ls -lh
RUN pip install ytdl_sub-0.0.1-py3-none-any.whl

###############################################################################
# S6 OVERLAY

ARG S6_OVERLAY_VERSION=3.1.0.1

ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz
ENTRYPOINT ["/init"]




