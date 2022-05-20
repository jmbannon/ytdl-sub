# Running ytdl-sub in Docker
The ytdl-sub docker image uses
[LinuxServer's](https://www.linuxserver.io/)
[base alpine image](https://github.com/linuxserver/docker-baseimage-alpine).
It looks, feels, and operates like other LinuxServer.io images.

The image will install ytdl-sub as a python package, and can be used
via command line with `ytdl-sub`.

## Building Locally
Run `make docker` in the root directory of this repo to build the image. This
will build the python wheel and install it in the Dockerfile.

## Usage
### docker-compose
```yaml
version: "2.1"
services:
  ytdl-sub:
    image: ytdl-sub:latest
    container_name: ytdl-sub
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Los_Angeles
    volumes:
      - <path/to/ytdl-sub/config>:/config
      - <path/to/tv_shows>:/tv_shows # optional
      - <path/to/movies>:/movies # optional
      - <path/to/music_videos>:/music_videos # optional
      - <path/to/music>:/music # optional
    restart: unless-stopped
```
### docker cli
```commandline
docker run -d \
    --name=ytdl-sub \
    -e PUID=1000 \
    -e PGID=1000 \
    -e TZ=America/Los_Angeles \
    -v <path/to/ytdl-sub/config>:/config \
    -v <OPTIONAL/path/to/tv_shows>:/tv_shows \
    -v <OPTIONAL/path/to/movies>:/movies \
    -v <OPTIONAL/path/to/music_videos>:/music_videos \
    -v <OPTIONAL/path/to/music>:/music \
    --restart unless-stopped \
    ytdl-sub:latest
```