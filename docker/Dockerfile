FROM ghcr.io/linuxserver/baseimage-alpine:3.15

USER ${PUID}:${PGID}
COPY . .

RUN apk add --no-cache --upgrade \
    python3=3.10.4-r0            \
    pip3=22.0.4-r0

RUN pip install -e .


