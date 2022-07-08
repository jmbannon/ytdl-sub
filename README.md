# ytdl-sub: Youtube-DL-Subscribe
[<img src="https://img.shields.io/badge/readthedocs-link-blue?logo=readthedocs">](https://ytdl-sub.readthedocs.io/en/latest/index.html)
![Checks](https://img.shields.io/github/checks-status/jmbannon/ytdl-sub/master)
![Code Coverage](https://img.shields.io/codecov/c/github/jmbannon/ytdl-sub)
![Code Qaulity](https://img.shields.io/badge/pylint-10%2F10-brightgreen)
![License](https://img.shields.io/github/license/jmbannon/ytdl-sub?color=blue)


Automate downloading and adding metadata with YoutubeDL.

This package downloads media via 
[yt-dlp](https://github.com/yt-dlp/yt-dlp)
and prepares it for your favorite media player
([Kodi](https://github.com/xbmc/xbmc), 
[Jellyfin](https://github.com/jellyfin/jellyfin), 
[Plex](https://github.com/plexinc/pms-docker),
[Emby](https://github.com/plexinc/pms-docker),
modern music players).

We recognize that everyone stores their 
media differently. Our approach for file and metadata formatting is to provide
maximum flexibility while maintaining simplicity.

## How it Works
`ytdl-sub` uses YAML configs to define a layout for how you want media to look
after it is downloaded. See our
[example configurations](https://github.com/jmbannon/ytdl-sub/tree/master/examples)
that we personally use and
[readthedocs](https://ytdl-sub.readthedocs.io/en/latest/config.html#)
for detailed information on specific sections or fields.

Once configured, you can begin downloading using two different methods.

### Subscription
You can define a `subscriptions.yaml` for things to recurrently
download, like a YouTube channel to pull new videos. It looks something like:
```yaml
john_smith_channel:
  preset: "yt_channel_as_tv"
  youtube:
    channel_url: "https://youtube.com/channe/UCsvn_Po0SmunchJYtttWpOxMg"
  overrides:
    tv_show_name: "John Smith Vlogs"
```
The download can be performed using:
```shell
ytdl-sub sub subscription.yaml
```

### One-time Download
There are things we will only want to download once and never again. Anything
you can define in a subscription can be defined using CLI arguments. This
example is equivalent to the subscription example above:
```shell
ytdl-sub dl \
    --preset "yt_channel_as_tv" \
    --youtube.channel_url "https://youtube.com/channel/UCsvn_Po0SmunchJYtttWpOxMg" \
    --overrides.tv_show_name "John Smith Vlogs"
```

### Output
After `ytdl-sub` runs, the end result will download and format the channel
files into something ready to be consumed by your favorite media player or
server. The `--dry-run` flag can be used to view file output before any downloading occurs.
```
/path/to/youtube_tv_shows/John Smith Vlogs
  /Season 2021
    s2021.e0317 - St Pattys Day Video-thumb.jpg
    s2021.e0317 - St Pattys Day Video.mp4
    s2021.e0317 - St Pattys Day Video.nfo
  /Season 2022
    s2022.e1225 - Merry Christmas-thumb.jpg
    s2022.e1225 - Merry Christmas.mp4
    s2022.e1225 - Merry Christmas.nfo
  poster.jpg
  fanart.jpg
  tvshow.nfo
```

## Installation

The ytdl-sub docker image uses
[LinuxServer's](https://www.linuxserver.io/)
[base alpine image](https://github.com/linuxserver/docker-baseimage-alpine).
It looks, feels, and operates like other LinuxServer images. This is the 
recommended way to use ytdl-sub.

### Docker Compose
```yaml
version: "2.1"
services:
  ytdl-sub:
    image: ghcr.io/jmbannon/ytdl-sub:latest
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
### Docker CLI
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
    ghcr.io/jmbannon/ytdl-sub:latest
```

### Building Docker Image Locally
Run `make docker` in the root directory of this repo to build the image. This
will build the python wheel and install it in the Dockerfile.

### Virtualenv
With a Python 3.10 virtual environment, you can clone and install the repo using
```commandline
git clone https://github.com/jmbannon/ytdl-sub.git
cd ytdl-sub

pip install -e .
```

## Contributing
There are many ways to contribute, even without coding. Please take a look in
our [Github Issues](https://github.com/jmbannon/ytdl-sub/issues) to ask
questions, submit a feature request, or pick up a bug.
