# ytdl-sub: Youtube-DL-Subscribe
[<img src="https://img.shields.io/badge/readthedocs-link-blue?logo=readthedocs">](https://ytdl-sub.readthedocs.io/en/latest/index.html)
![Checks](https://img.shields.io/github/checks-status/jmbannon/ytdl-sub/master)
![Code Coverage](https://img.shields.io/codecov/c/github/jmbannon/ytdl-sub)
![Code Qaulity](https://img.shields.io/badge/pylint-10%2F10-brightgreen)
![License](https://img.shields.io/github/license/jmbannon/ytdl-sub?color=blue)


Automate downloading and adding metadata with YoutubeDL.

This package downloads media via 
[yt-dlp](https://github.com/yt-dlp/yt-dlp)
and prepares it for consumption in your favorite media player
([Kodi](https://github.com/xbmc/xbmc), 
[Jellyfin](https://github.com/jellyfin/jellyfin), 
[Plex](https://github.com/plexinc/pms-docker),
[Emby](https://github.com/plexinc/pms-docker),
modern music players).

We recognize that everyone stores their 
media differently. Our approach for file and metadata formatting is to provide
maximum flexibility while maintaining simplicity. Read more about it
[here](https://ytdl-sub.readthedocs.io/en/latest/getting_started.html).

## Supported Features
Below lists supported download schemes. You can see our
[various example configurations](https://github.com/jmbannon/ytdl-sub/tree/master/examples)
to get an idea on how to use ytdl-sub to your liking.

- Download any and all audio/video from a channel or playlist
  - Format videos to look like
    - Movies
    - TV Shows
    - TV Show Seasons
    - Music Videos
  - Format and tag audio files to look like
    - Albums, Singles
    - Audiobooks
  - Download thumbnails, channel avatars, and banners to set as
    - Posters
    - Fanart
    - Banners
    - Album Artwork
- Download a soundcloud artist's albums and singles
  - Format the music tags and save any artwork for album covers
- Manually download a single audio/video file
  - Reuse configs you have defined to format it as anything you like
- Only download recent audio/video, optionally remove old files


## Configuration
Formatting video and audio files are defined by presets. The `{variables}` used
in the strings are derived from the media itself or defined by you in the `overrides`
section. Below shows what a `config.yaml` and `subscription.yaml` look like to 
download a Youtube channel as a TV show with artwork. The files are formatted
to look like:
```
/path/to/youtube_tv_shows/Your Favorite YT Channel
  /Season 2021
    s2021.e0317 - St Pattys Day Video.jpg
    s2021.e0317 - St Pattys Day Video.mp4
    s2021.e0317 - St Pattys Day Video.nfo
  /Season 2022
    s2022.e1225 - Merry Christmas.jpg
    s2022.e1225 - Merry Christmas.mp4
    s2022.e1225 - Merry Christmas.nfo
  poster.jpg
  fanart.jpg
  tvshow.nfo
```

### config.yaml
The config file defines _how_ to download and format media. You can define any
number of presets to represent media how you see fit.
```yaml
configuration:
  working_directory: '.ytdl-sub-downloads'

presets:
  yt_channel_as_tv:
    youtube:
      download_strategy: "channel"
      channel_avatar_path: "poster.jpg"
      channel_banner_path: "fanart.jpg"

    # Pass any ytdl parameter to the downloader. It is recommended to leave
    # ignoreerrors=True for things like age-restricted or hidden videos.
    ytdl_options:
      ignoreerrors: True

    output_options:
      output_directory: "{youtube_tv_shows_directory}/{tv_show_name_sanitized}"
      file_name: "{episode_name}.{ext}"
      thumbnail_name: "{episode_name}.jpg"
      maintain_download_archive: True

    convert_thumbnail:
      to: "jpg"

    nfo_tags:
      nfo_name: "{episode_name}.nfo"
      nfo_root: "episodedetails"
      tags:
        title: "{title}"
        season: "{upload_year}"
        episode: "{upload_month}{upload_day_padded}"
        plot: "{description}"
        year: "{upload_year}"
        aired: "{upload_date_standardized}"

    output_directory_nfo_tags:
      nfo_name: "tvshow.nfo"
      nfo_root: "tvshow"
      tags:
        title: "{tv_show_name}"

    overrides:
      youtube_tv_shows_directory: "/path/to/youtube_tv_shows"
      episode_name: "Season {upload_year}/s{upload_year}.e{upload_month_padded}{upload_day_padded} - {title_sanitized}"
```

#### subscription.yaml
The subscription file defines _what_ to download. Anything in the preset can be
overwritten by a subscription.

```yaml
# Downloads the entire channel
john_smith_archive:
  preset: "yt_channel_as_tv"
  youtube:
    channel_id: "UCsvn_Po0SmunchJYtttWpOxMg"
  # Any user-defined override variables will automatically create a `_sanitized`
  # variable name, which is safe to use for file names and paths.
  # In this example, `tv_show_name` will produce `tv_show_name_sanitized` 
  overrides:
    tv_show_name: "John /\ Smith"

# Downloads and only keeps videos uploaded in the last 2 weeks
john_doe_recent_archive:
  preset: "yt_channel_as_tv"
  youtube:
    channel_id: "UCsvn_Po0SmunchJYtttWpOxMg"
    after: "today-2weeks"
  overrides:
    tv_show_name: "John /\ Smith"
  # Will stop looking at channel videos if it already exists or the upload date
  # is out of range
  ytdl_options:
    break_on_existing: True
    break_on_reject: True
  output_options:
    keep_files:
      after: "today-2weeks"
```

## Usage
You can have multiple subscription files for better organizing. We can invoke
the subscription download using the command below. For cron jobs, this is the
recommended command to use.
```shell
ytdl-sub sub subscription.yaml
```

### One-time Downloads
There are things we want to download, but not subscribe to. In this case, you
can invoke `ytdl-sub dl` and add any fields like a subscription. This example is
equivalent to using the subscription yaml above, but without the yaml.
```shell
ytdl-sub dl                                             \
    --preset "yt_channel_as_tv"                         \
    --youtube.channel_id "UCsvn_Po0SmunchJYtttWpOxMg"   \
    --overrides.tv_show_name "John /\ Smith"
```

## Installation
Once we are ready for our first release, we will add this package to pypi. Then,
we plan to create a docker image that uses the
[LinuxServer.io](https://www.linuxserver.io/)
base image, and hopefully become a part of their fleet someday.

Until then, you will have to clone this repo and run it using python 3.10
```commandline
git clone https://github.com/jmbannon/ytdl-sub.git
cd ytdl-sub

pip install -e .
```

## Additional Documentation
We are actively working on documenting all ytdl-sub features
[within our readthedocs page](https://ytdl-sub.readthedocs.io/en/latest/).
It is still a work-in-progress, but you can still find some useful things
in there.

## Contributing
There are many ways to contribute, even without coding. Please take a look in
our [Github Issues](https://github.com/jmbannon/ytdl-sub/issues) to ask
questions, submit a feature request, or pick up a bug. I try to be responsive
and provide constructive PR feedback to maintain excellent code quality ;)