# ytdl-sub
## Automate downloading and metadata generation with YoutubeDL.
[<img src="https://img.shields.io/badge/readthedocs-link-blue?logo=readthedocs">](https://ytdl-sub.readthedocs.io/en/latest/index.html)
[<img src="https://img.shields.io/discord/994270357957648404?logo=Discord">](https://discord.gg/v8j9RAHb4k)
[![codecov](https://img.shields.io/codecov/c/github/jmbannon/ytdl-sub)](https://app.codecov.io/gh/jmbannon/ytdl-sub)
![Code Qaulity](https://img.shields.io/badge/pylint-10%2F10-brightgreen)
![Checks](https://img.shields.io/github/checks-status/jmbannon/ytdl-sub/master)
![License](https://img.shields.io/github/license/jmbannon/ytdl-sub?color=blue)

`ytdl-sub` is a command-line tool that downloads media via 
[yt-dlp](https://github.com/yt-dlp/yt-dlp)
and prepares it for your favorite media player, including
[Kodi](https://github.com/xbmc/xbmc), 
[Jellyfin](https://github.com/jellyfin/jellyfin), 
[Plex](https://github.com/plexinc/pms-docker),
[Emby](https://emby.media/),
and modern music players. No additional plugins or external scrapers are needed.

We recognize that everyone stores their 
media differently. Our approach for file and metadata formatting is to provide
maximum flexibility while maintaining simplicity.

### YouTube Channels as TV Shows
#### Plex
![unknown](https://user-images.githubusercontent.com/10107080/202107286-d8f38c7b-7caf-413a-b9a3-0bbbaded3646.png)

#### Jellyfin
![jellyfin](https://user-images.githubusercontent.com/10107080/182677243-b4184e51-9780-4094-bd40-ea4ff58555d0.PNG)

### Music Videos and Concerts
#### Kodi
![kodi](https://user-images.githubusercontent.com/10107080/182677268-d1bf2ff0-9b9c-4a04-98ec-443a67ada734.png)
#### Jellyfin
![jelly_mv](https://user-images.githubusercontent.com/10107080/182677256-43aeb029-0c3f-4648-9fd2-352b9666b262.PNG)

### SoundCloud Discography
#### Writes proper music-tags via beets API
![sc_mb](https://user-images.githubusercontent.com/10107080/182685415-06adf477-3dd3-475d-bbcd-53b0152b9f0a.PNG)

### Bandcamp Discography
![bc_nav](https://user-images.githubusercontent.com/10107080/212503861-1d8748e6-6f6d-4043-b543-84226cd1f662.png)

## How it Works
`ytdl-sub` uses YAML files to define subscriptions. Each subscription imports _presets_ that
define how to handle and output media files. `ytdl-sub` comes packaged with many _prebuilt presets_
that do the work of config-building, so you can start downloading immediately.

```yaml
# subscriptions.yaml:
# Everything in here can be downloaded using the command:
#   ytdl-sub sub subscriptions.yaml

# __preset__ is a place to define global overrides for all subscriptions
__preset__:
  overrides:
    # Root folder of all ytdl-sub TV Shows
    tv_show_directory: "/tv_shows"
    
    # Root folder of all ytdl-sub Music
    music_directory: "/music"
    
    # Root folder of all ytdl-sub Music Videos
    music_video_directory: "/music_videos"
    
    # For 'Only Recent' preset, only keep vids within this range and limit
    only_recent_date_range: "2months"
    only_recent_max_files: 30
    
  # Pass any arg directly to yt-dlp's Python API
  ytdl_options:
    cookiefile: "/config/cookie.txt" 

###################################################################
# TV Show Presets. Can replace Plex with Plex/Jellyfin/Kodi

Plex TV Show by Date:

  # Sets genre tag to "Documentaries"
  = Documentaries:
    "NOVA PBS": "https://www.youtube.com/@novapbs"
    "National Geographic": "https://www.youtube.com/@NatGeo"
    "Cosmos - What If": "https://www.youtube.com/playlist?list=PLZdXRHYAVxTJno6oFF9nLGuwXNGYHmE8U"

  # Sets genre tag to "Kids", "TV-Y" for content rating
  = Kids | = TV-Y:
    "Jake Trains": "https://www.youtube.com/@JakeTrains"
    "Kids Toys Play": "https://www.youtube.com/@KidsToysPlayChannel"

  = Music:
    # TV show subscriptions can support multiple urls and store in the same TV Show
    "Rick Beato":
      - "https://www.youtube.com/@RickBeato"
      - "https://www.youtube.com/@rickbeato240"

  # Set genre tag to "News", use `Only Recent` preset to only store videos uploaded recently
  = News | Only Recent:
    "BBC News": "https://www.youtube.com/@BBCNews"

Plex TV Show Collection:
  = Music:
    # Prefix with ~ to set specific override variables
    "~Beyond the Guitar":
      s01_name: "Videos"
      s01_url: "https://www.youtube.com/c/BeyondTheGuitar"
      s02_name: "Covers"
      s02_url: "https://www.youtube.com/playlist?list=PLE62gWlWZk5NWVAVuf0Lm9jdv_-_KXs0W"

###################################################################
# Music Presets. Can replace Plex with Plex/Jellyfin/Kodi

YouTube Releases:
  = Jazz:  # Sets genre tag to "Jazz"
    "Thelonious Monk": "https://www.youtube.com/@theloniousmonk3870/releases"

YouTube Full Albums:
  = Lofi:
    "Game Chops": "https://www.youtube.com/playlist?list=PLBsm_SagFMmdWnCnrNtLjA9kzfrRkto4i"

SoundCloud Discography:
  = Chill Hop:
    "UKNOWY": "https://soundcloud.com/uknowymunich"
  = Synthwave:
    "Lazerdiscs Records": "https://soundcloud.com/lazerdiscsrecords"
    "Earmake": "https://soundcloud.com/earmake"

Bandcamp:
  = Lofi:
    "Emily Hopkins": "https://emilyharpist.bandcamp.com/"

###################################################################
# Music Video Presets
"Plex Music Videos":
  = Pop:  # Sets genre tag to "Pop"
    "Rick Astley": "https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"
    "Michael Jackson": "https://www.youtube.com/playlist?list=OLAK5uy_mnY03zP6abNWH929q2XhGzWD_2uKJ_n8E"
```

All of this can be downloaded and ready to import to your favorite player 
using the command
```commandline
ytdl-sub sub subscriptions.yaml
```
See our
[example subscriptions](https://github.com/jmbannon/ytdl-sub/tree/master/examples)
for more detailed examples and use-cases.

### Output
After `ytdl-sub` runs, the end result will download and format the files into something ready 
to be consumed by your favorite media player/server.
```
tv_shows/
  Jake Trains/
    Season 2021/
      s2021.e031701 - Pattys Day Video-thumb.jpg
      s2021.e031701 - Pattys Day Video.mp4
      s2021.e031701 - Pattys Day Video.nfo
      s2021.e031702 - Second Pattys Day Video-thumb.jpg
      s2021.e031702 - Second Pattys Day Video.mp4
      s2021.e031702 - Second Pattys Day Video.nfo
    Season 2022/
      s2022.e122501 - Merry Christmas-thumb.jpg
      s2022.e122501 - Merry Christmas.mp4
      s2022.e122501 - Merry Christmas.nfo
    poster.jpg
    fanart.jpg
    tvshow.nfo

music/
  Artist/
    [2022] Some Single/
      01 - Some Single.mp3
      folder.jpg
    [2023] Latest Album/
      01 - Track Title.mp3
      02 - Another Track.mp3
      folder.jpg

music_videos/
  Elton John/
    Elton John - Rocketman.jpg
    Elton John - Rocketman.mp4
```

## Custom Configs
Any part of this process is modifiable by using custom configs. See our
[walk-through guide](https://ytdl-sub.readthedocs.io/en/latest/guides/index.html)
on how to build your first config from scratch. Ready-to-use
[example configurations](https://github.com/jmbannon/ytdl-sub/tree/master/examples)
can be found here alongside our
[readthedocs](https://ytdl-sub.readthedocs.io/en/latest/index.html)
for detailed information on all config fields.

## Installation
`ytdl-sub` can be installed on the following platforms.

- [Docker Compose](https://ytdl-sub.readthedocs.io/en/latest/guides/install/docker.html#install-with-docker-compose)
  - [Web-GUI](https://ytdl-sub.readthedocs.io/en/latest/guides/install/docker.html#install-with-docker-compose)
  - [Headless](https://ytdl-sub.readthedocs.io/en/latest/guides/install/docker.html#install-with-docker-compose)
  - [CPU / GPU Passthrough](https://ytdl-sub.readthedocs.io/en/latest/guides/install/docker.html#device-passthrough)
- [Docker CLI](https://ytdl-sub.readthedocs.io/en/latest/guides/install/docker.html#docker-cli)
- [Windows](https://ytdl-sub.readthedocs.io/en/latest/guides/install/windows.html)
- [Unraid](https://ytdl-sub.readthedocs.io/en/latest/guides/install/unraid.html)
- [Linux](https://ytdl-sub.readthedocs.io/en/latest/guides/install/linux.html)
- [Linux ARM](https://ytdl-sub.readthedocs.io/en/latest/guides/install/linux.html)
- [PIP](https://ytdl-sub.readthedocs.io/en/latest/guides/install/agnostic.html#pip-install)
- [Local Install](https://ytdl-sub.readthedocs.io/en/latest/guides/install/agnostic.html#local-install)
- [Local Docker Build](https://ytdl-sub.readthedocs.io/en/latest/guides/install/agnostic.html#local-docker-build)

### Docker Installation
Docker installs can be either headless or use the Web-GUI image, which comprises
[LSIO's](https://www.linuxserver.io/)
[code-server](https://hub.docker.com/r/linuxserver/code-server)
Docker image with `ytdl-sub` preinstalled. This is the recommended way to use ``ytdl-sub``.

![image](https://github.com/jmbannon/ytdl-sub/assets/10107080/c2aac8a1-5443-4345-b438-be4b17187c80)


## Contributing
There are many ways to contribute, even without coding. Please take a look in
our [GitHub Issues](https://github.com/jmbannon/ytdl-sub/issues) to submit a feature request, or 
pick up a bug.

## Support
We are pretty active in our
[Discord channel](https://discord.gg/v8j9RAHb4k)
if you have any questions. Also see our
[FAQ](https://ytdl-sub.readthedocs.io/en/latest/faq/index.html)
for commonly asked questions.
