# YoutubeDL-Subscribe
Automate downloading and adding metadata with YoutubeDL.

The motivation behind this package is to download media via [youtube-dlp](https://github.com/yt-dlp/yt-dlp)
and prepare it for consumption in your favorite media player in the most hassle-free way possible. 

Everyone stores their media differently, so it is critical to provide comprehensive customization to this process
while maintaining simplicity. In addition, we treat media sources differently from each other. We may want to...

- Automatically download any and all audio/video file from a channel, user, playlist, etc. 
  - Download a soundcloud artist's discography, keep it up to date
  - Download any new music videos from a YouTube channel playlist
- Manually download a single audio/video file
  - Download one particular music video
- Only download recent audio/video, and remove stale files
  - Download and only keep recent podcasts, news videos

We want to cover each of these use cases.

## Configuration
Below is the proposed way to define a `preset` for how you want to download and add metadata. We have two examples,
one for downloading Soundcloud discographies, and the other for downloading YouTube playlists, and treating them as
music videos. Both are intended to be consumed by [Kodi](https://github.com/xbmc/xbmc), 
[Jellyfin](https://github.com/jellyfin/jellyfin), and any mp3 music player that supports id3v2.4 tags. For videos, this
should (hopefully) be customizable enough to support other use-cases like downloading a playlist as a TV show or
multiple movies.

#### config.yaml
```yaml
presets:
  # [Required]
  # Custom name that you define for your preset. This preset is intended to download
  # a soundcloud artist's discography.
  soundcloud_discography:
    
    # [Required]
    # This section defines the source you intend on using, with specific
    # configurations for each source. Supports [soundcloud, youtube]
    soundcloud:
      
      # [Required]
      # How to download media from the source, soundcloud supports [albums_and_singles]
      download_strategy: "albums_and_singles"
      
      # [Optional] 
      # Each source has specific options, this is one for soundcloud that skips
      # premiere tracks
      skip_premiere_tracks: True
      
      # [Required, defined dynamically]
      # The username of the soundcloud artist you want to download from
      # username: alis_on
      
    # [Optional]
    # Defines any arguments you want to directly pass to yt_dlp. Use with caution!
    ytdl_options:
      
      # For my case, I want the best audio converted to mp3
      format: 'bestaudio[ext=mp3]'
    
    # [Required]
    # This section defines where and how you want to save files
    output_options:
      
      # [Required]
      # Directory for where you want all your files to land for this preset
      output_directory: "{music_path}/{sanitized_artist}"
      
      # [Required]
      # How you want to name each file that gets downloaded in this preset
      file_name: "[{album_year}] {sanitized_album}/{track_number_padded} - {sanitized_title}.{ext}"
      
      # [Optional]
      # If a thumbnail is available, convert it to your desired file type (webp, ugh)
      convert_thumbnail: "jpg"
      
      # [Optional]
      # If you want to store a thumbnail, define how it gets named
      thumbnail_name: "[{album_year}] {sanitized_album}/folder.jpg"
    
    # [Optional]
    # Define how you want to add metadata to your downloaded media
    metadata_options:
      
      # [Optional]
      # If your final file is mp3, add id3 tags (TODO: support for more file types)
      id3_tags:
        
        # [Optional]
        # id3 version, defaults to 2.4
        id3_version: 2.4
        
        # [Optional]
        # For 2.4 multi-tags, define which character to use for the null separator
        null_separator_char: ";"
        
        # [Required]
        # Define the tag names and values to add to your audio
        tags:
          artist: "{artist}"
          albumartist: "{artist}"
          title: "{title}"
          album: "{album}"
          tracknumber: "{track_number}"
          year: "{album_year}"
          genre: "{genre}"

    # [Optional]
    # This will lazily add/override any media variable that can be used in
    # output or metadata options
    overrides:
      
      # Notice how we use music_path in the output_options.output_directory field above
      music_path: "/mnt/nas/music"

  ######################################################################################
  # Another preset, intended to download all music videos in a YouTube playlist.
  youtube_music_video_playlist:
    
    # [Required]
    # Our source is YouTube, so define the youtube section.
    youtube:
      
      # [Required]
      # Download strategies are different for each source. For YouTube, we want to
      # download the whole playlist (also the only supported download_strategy for now).
      download_strategy: "playlist"
      
      # [Required, defined dynamically]
      # The YouTube playlist id you want to download from
      # playlist_id: "PLVTLbc6i-h_iuhdwUfuPDLFLXG2QQnz-x"
    
    # [Optional]
    ytdl_options:
      # In my case, I want the best format possible, and ignore any errors like
      # geo/age restricted videos.
      format: 'best'
      ignoreerrors: True
    
    # [Required]
    output_options:
      
      # Notice in my overrides, I defined the both music_video_path and kodi_music_video_name.
      output_directory: "{music_video_path}"
      file_name: "{kodi_music_video_name}.{ext}"
      convert_thumbnail: "jpg"
      thumbnail_name: "{kodi_music_video_name}.jpg"
    
    # [Optional]
    metadata_options:
  
      # [Optional]
      # Kodi works with NFO files for videos. I want to format this to be read in as a music video
      nfo:
        
        # [Required]
        # Name of the nfo file
        nfo_name: "{kodi_music_video_name}.nfo"
        
        # [Required]
        # Inside the nfo XML, define the root section.
        nfo_root: "musicvideo"
        
        # [Required]
        # Within the nfo root, define any tags you want set
        tags:
          artist: "{artist}"
          title: "{title}"
          album: "Music Videos"
          year: "{upload_year}"
    
    # [Optional]
    overrides:
      
      # I personally like my paths defined explicitly as variables.
      music_video_path: "/mnt/nas/music"
      
      # Kodi wants music videos all in one folder, named like 'artist - title'
      # This format is used for the video file, thumbnail, and nfo file. So
      # create a shared variable that each of them will use.
      kodi_music_video_name: "{sanitized_artist} - {sanitized_title}"
```

## Usage
That was a lot! If you have made it this far, thanks for your interest. Now we can see how to use our presets to
actually download. There are three methods this project aims to build.

### Subscriptions
Defining a subscription is for media that you will continually want to download, whether that be performed manually
or in a cron job. We implement this by defining yet another yaml.

#### subscription.yaml
```yaml
# [Required]
# Custom name that you define for your subscription. Any fields defined here will override anything defined in the
# preset.
ALISON:
  
  # [Required]
  # Name of the preset to use
  preset: "soundcloud_discography"
  
  # We did not define soundcloud.username in the preset on purpose, so we can define it here
  soundcloud:
    username: alis_on
  
  # For this artist, I want to explicitly define the artist name and genres that will get used in the metadata
  # and output paths. An implicit feature is all overrides also create a sanitized variable as well. So
  # `sanitized_artist` can be used, and will run the sanitize function on my artist override.
  overrides:
    artist: "A.L.I.S.O.N."
    genre: "Synthwave;Electronic;Instrumental"

######################################################################################
# Another subscription that can use a different preset, overrides, etc.
Rammstein:

  # [Required]
  preset: "youtube_music_video_playlist"
  
  # [Required]
  # We did not define youtube.playlist_id in the preset on purpose, to define it here.
  youtube:
    playlist_id: "PLVTLbc6i-h_iuhdwUfuPDLFLXG2QQnz-x"
  
  # [Optional]
  overrides:
    artist: "Rammstein"
```

You can have multiple subscription files for better organizing. We can invoke the subscriptoin download
using the command below. This makes it easy to use `ytdl-sub` in a cron job.
```shell
ytdl-sub sub subscription.yaml
```

### One-time Downloads [not available yet]
There are things I want to download, but not subscribe to. In this case, I can invoke `ytdl-sub dl` and add any
required/optional/override fields. This example is equivalent to using the subscription yaml above, but without
the yaml.
```shell
ytdl-sub dl                                                \
    --preset "soundcloud_discography"                      \
    --soundcloud.username "alis_on"                        \
    --overrides.artist "A.L.I.S.O.N."                      \
    --overrides.genre "Synthwave;Electronic;Instrumental"

```

### REST API [not available yet]
The dream will be to create mobile apps or browser extensions to invoke downloads from the couch. My short-term
plan is to self-host a swaggerhub io instance and invoke the rest api from my browser. It will be a while before
this gets implemented, but when it does, it will look like this.
```commandline
# spin-up the server
ytdl-sub server
```
POST request to invoke the same one-time download example via REST.
```commandline
curl -X POST -H "Content-type: application/json"                \
    -d '{                                                       \
        "soundcloud.username": "alis_on",                       \
        "overrides.artist": "A.L.I.S.O.N.",                     \
        "overrides.genre": "Synthwave;Electronic;Instrumental"  \
    }'                                                          \
    'localhost:8080/soundcloud_discography'
```

## Other Nice-To-Have Feature Ideas [not available yet]
### Check existing media before downloading
Right now, ytdl-sub will naively download everything in the given playlist/artist url. We should check the destination
directory first to see if it has already been downloaded. Might involve including a tag with its ytdl id.

### More download strategies
Only full artist (soundcloud) and playlists (youtube) are currently supported. Add new ones for single song/video
downloads.

### Make adding new sources easy to implement
Developers should not have to work around spaghetti to add new sources to ytdl-subscribe. It should be very modularized
and definable in a separate file as a plugin.

### Musicbrainz Integration
Integration with musicbrainz to fetch correct artist names, song titles, ids, etc and make those tags usable would be
a great feature for OCD music hoarders like myself, and would play nicely with existing collections to ensure
files land in the same directory. This can be worked around for now by using overrides.

### Configurable Time Windows to Delete Stale Media
There are some news channels and podcasts that I'd like to download but only keep the prior 2 weeks-worth of videos.
This would have to introspect files that reside in the host filesystem. Extreme caution would be required since we are
perma-deleting files.

## Contributing
I would like to get this to a point where I create a stable release before I accept PRs from the outside world. In the
meantime, any feedback in the form of a Github issue would be greatly appreciated and taken into consideration.