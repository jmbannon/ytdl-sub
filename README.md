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

### SoundCloud Albums and Singles
#### MusicBee (any file or tag-based music players)
![sc_mb](https://user-images.githubusercontent.com/10107080/182685415-06adf477-3dd3-475d-bbcd-53b0152b9f0a.PNG)

### Bandcamp Discography
#### Navidrome (any file or tag-based music servers)
![bc_nav](https://user-images.githubusercontent.com/10107080/212503861-1d8748e6-6f6d-4043-b543-84226cd1f662.png)


## How it Works
`ytdl-sub` uses YAML configs to define a layout for how you want media to look
after it is downloaded. See our
[walk-through guide](https://github.com/jmbannon/ytdl-sub/wiki)
on how to get started. Ready-to-use
[example configurations](https://github.com/jmbannon/ytdl-sub/tree/master/examples)
can be found here alongside our
[readthedocs](https://ytdl-sub.readthedocs.io/en/latest/config.html#)
for detailed information on config fields.


### Config
The `config.yaml` defines how our downloads will look. For this example, let us
download YouTube channels and generate metadata to look like TV shows using
ytdl-sub's prebuilt presets. No additional plugins or programs are needed for
Kodi, Jellyfin, Plex, or Emby to recognize your downloads. This can also be
used to download any yt-dlp supported URL, including YouTube playlists, Bitchute channels, etc.


```yaml
# Set the working directory which will be used to stage downloads
# before placing them in your desired output directory.
configuration:
  working_directory: '.ytdl-sub-downloads'

# Presets are where you create 'sub-configs' that can can be
# merged together to dictate what is downloaded, how to format it,
# and what metadata to generate.
presets:

  # Let us create a preset called `only_recent_videos` that will
  # only download recent videos in the last 2 months.
  only_recent_videos:

    # Use the `date_range` plugin to specify ytdl-sub to only
    # download videos after today MINUS {download_range}, which
    # is an override variable that we can alter per channel.
    date_range:
      after: "today-{download_range}"

    # Any yt-dlp argument can be passed via ytdl-sub. Let us set
    # yt-dlp's `break_on_reject` to True to stop downloading after
    # any video is rejected. Videos will be rejected if they are
    # uploaded after our {download_range}.
    ytdl_options:
      break_on_reject: True

    # Deletes any videos uploaded after {download_range}.
    output_options:
      keep_files_after: "today-{download_range}"

    # Set the override variable {download_range} to 2months.
    # This will serve as our default value. We can override
    # this per channel or in a child preset.
    overrides:
      download_range: "2months"

  ####################################################################

  # Now let us create a preset that downloads videos and formats
  # as TV shows.
  tv_show:

    # Presets can inherit all attributes from other presets. Our
    # `tv_show` preset will inherit these presets built into ytdl-sub.
    preset:
      # Let us specify all the TV show by date presets to support all
      # players. You only need to specify one, but this ensures
      # compatibility with all players.
      - "kodi_tv_show_by_date"
      - "jellyfin_tv_show_by_date"
      - "plex_tv_show_by_date"
      # Now we choose a preset that defines how our seasons and
      # episode numbers look.
      - "season_by_year__episode_by_month_day"

    # Set override variables that will be applicable to all downloads
    # in main presets.
    overrides:
      tv_show_directory: "/tv_shows"  # Replace with desired directory

```

### Subscriptions
The `subscriptions.yaml` file is where we define content to download using
presets in the `config.yaml`. Each subscription can overwrite any field used
in a preset.
```yaml
# The name of our subscription. Let us create one to download
# ALL of Rick A's videos
rick_a:
  # Inherit our `tv_show` preset we made above
  preset:
    - "tv_show"
  
  # Set override variables to set the channel URL and the
  # name we want to give the TV show.
  overrides:
    tv_show_name: "Rick A"
    url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"

# Let us make another subscription that will only download Rick A's
# video's in the last 2 weeks.
rick_a_recent:
  # Inherit our `tv_show` AND `only_recent_videos` preset
  # Bottom-most presets take precedence.
  preset:
    - "tv_show"
    - "only_recent_videos"
  
  # Set override variables for this subscription. Modify the
  # `download_range` to only download and keep 2 weeks' worth
  # of videos.
  overrides:
    tv_show_name: "Rick A"
    url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
    download_range: "2weeks"

```
The download can now be performed using:
```shell
ytdl-sub sub subscriptions.yaml
```
To preview what your output files before doing any downloads, you can dry run using:
```shell
ytdl-sub --dry-run sub subscriptions.yaml
```

### One-time Download
There are things we will only want to download once and never again. Anything
you can define in a subscription can be defined using CLI arguments. This
example is equivalent to the subscription example above:
```shell
ytdl-sub dl \
    --preset "tv_show" \
    --overrides.tv_show_name "Rick A" \
    --overrides.url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
```

#### Download Aliases
In the `config.yaml`, we can define aliases to make `dl` commands shorter.
```yaml
configuration:
  dl_aliases:
    tv: "--preset tv_show"
    name: "--overrides.tv_show_name"
    url: "--overrides.url"
```
The above command can now be shortened to
```shell
ytdl-sub dl \
    --tv \
    --name "Rick A" \
    --url "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
```

### Output
After `ytdl-sub` runs, the end result will download and format the channel
files into something ready to be consumed by your favorite media player or
server.
```
/path/to/tv_shows/Rick Aß
  /Season 2021
    s2021.e0317 - Pattys Day Video-thumb.jpg
    s2021.e0317 - Pattys Day Video.mp4
    s2021.e0317 - Pattys Day Video.nfo
  /Season 2022
    s2022.e1225 - Merry Christmas-thumb.jpg
    s2022.e1225 - Merry Christmas.mp4
    s2022.e1225 - Merry Christmas.nfo
  poster.jpg
  fanart.jpg
  tvshow.nfo
```

### Beyond TV Shows
The above example made heavy-use of `ytdl-sub` prebuilt presets and hides many
features that are offered. `ytdl-sub` strives to support _any_ use case that first requires
a download via yt-dlp. Use `ytdl-sub` to download, format, and convert media for your media
player to recognize downloads as:
- Movies
- TV shows
  - From a single channel or playlist
  - From multiple channels or playlists
  - From individual videos
- Extracted audio as podcasts
- Music videos
- Music, including:
  - Individual songs
  - Albums
  - Discographies

## Installation
`ytdl-sub` can be installed on the following platforms.

- [Docker Compose](https://ytdl-sub.readthedocs.io/en/latest/install.html#docker-compose_)
- [Docker CLI](https://ytdl-sub.readthedocs.io/en/latest/install.html#docker)
- [Windows](https://ytdl-sub.readthedocs.io/en/latest/install.html#windows)
- [Linux](https://ytdl-sub.readthedocs.io/en/latest/install.html#linux)
- [Linux ARM](https://ytdl-sub.readthedocs.io/en/latest/install.html#linux-arm)
- [PIP](https://ytdl-sub.readthedocs.io/en/latest/install.html#pip)
- [Local Install](https://ytdl-sub.readthedocs.io/en/latest/install.html#local-install)
- [Local Docker Build](https://ytdl-sub.readthedocs.io/en/latest/install.html#local-docker-build)

## Contributing
There are many ways to contribute, even without coding. Please take a look in
our [GitHub Issues](https://github.com/jmbannon/ytdl-sub/issues) to submit a feature request, or 
pick up a bug.

## Support
We are pretty active in our
[Discord channel](https://discord.gg/v8j9RAHb4k)
if you have any questions. Also see our
[FAQ](https://github.com/jmbannon/ytdl-sub/wiki/FAQ)
for commonly asked questions.
