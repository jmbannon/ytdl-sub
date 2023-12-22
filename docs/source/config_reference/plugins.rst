Plugins
=======

audio_extract
-------------
Extracts audio from a video file.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       audio_extract:
         codec: "mp3"
         quality: 128

codec
~~~~~
The codec to output after extracting the audio. Supported codecs are aac, flac, mp3, m4a,
opus, vorbis, wav, and best to grab the best possible format at runtime.

quality
~~~~~~~
Optional. Specify ffmpeg audio quality. Insert a value between ``0`` (better) and ``9``
(worse) for variable bitrate, or a specific bitrate like ``128`` for 128k.

chapters
--------
Embeds chapters to video files if they are present. Additional options to add SponsorBlock
chapters and remove specific ones. Can also remove chapters using regex.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       chapters:
         # Embedded Chapter Fields
         embed_chapters: True
         allow_chapters_from_comments: False
         remove_chapters_regex:
           - "Intro"
           - "Outro"

         # Sponsorblock Fields
         sponsorblock_categories:
           - "outro"
           - "selfpromo"
           - "preview"
           - "interaction"
           - "sponsor"
           - "music_offtopic"
           - "intro"
         remove_sponsorblock_categories: "all"
         force_key_frames: False

allow_chapters_from_comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Optional. If chapters do not exist in the video/description itself, attempt to scrape
comments to find the chapters. Defaults to False.

embed_chapters
~~~~~~~~~~~~~~
Optional. Embed chapters into the file. Defaults to True.

force_key_frames
~~~~~~~~~~~~~~~~
Optional. Force keyframes at cuts when removing sections. This is slow due to needing a
re-encode, but the resulting video may have fewer artifacts around the cuts. Defaults to
False.

remove_chapters_regex
~~~~~~~~~~~~~~~~~~~~~
Optional. List of regex patterns to match chapter titles against and remove them from the
entry.

remove_sponsorblock_categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Optional. List of SponsorBlock categories to remove from the output file. Can only remove
categories that are specified in ``sponsorblock_categories`` or "all", which removes
everything specified in ``sponsorblock_categories``.

sponsorblock_categories
~~~~~~~~~~~~~~~~~~~~~~~
Optional. List of SponsorBlock categories to embed as chapters. Supports "sponsor",
"intro", "outro", "selfpromo", "preview", "filler", "interaction", "music_offtopic",
"poi_highlight", or "all" to include all categories.

date_range
----------
Only download files uploaded within the specified date range.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       date_range:
         before: "now"
         after: "today-2weeks"

after
~~~~~
Optional. Only download videos after this datetime.

before
~~~~~~
Optional. Only download videos before this datetime.

embed_thumbnail
---------------
Whether to embed thumbnails to the audio/video file or not.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       embed_thumbnail: True

file_convert
------------
Converts video files from one extension to another.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       file_convert:
         convert_to: "mp4"

Supports custom ffmpeg conversions:

.. code-block:: yaml

   presets:
     my_example_preset:
       file_convert:
         convert_to: "mkv"
         convert_with: "ffmpeg"
         ffmpeg_post_process_args: >
           -bitexact
           -vcodec copy
           -acodec copy
           -scodec mov_text

convert_to
~~~~~~~~~~
Convert to a desired file type. Supports:

* Video: avi, flv, mkv, mov, mp4, webm
* Audio: aac, flac, mp3, m4a, opus, vorbis, wav

convert_with
~~~~~~~~~~~~
Optional. Supports ``yt-dlp`` and ``ffmpeg``. ``yt-dlp`` will convert files within
yt-dlp whereas ``ffmpeg`` specifies it will be converted using a custom command specified
with ``ffmpeg_post_process_args``. Defaults to ``yt-dlp``.

ffmpeg_post_process_args
~~~~~~~~~~~~~~~~~~~~~~~~
Optional. ffmpeg args to post-process an entry file with. The args will be inserted in the
form of:

.. code-block:: bash

   ffmpeg -i input_file.ext {ffmpeg_post_process_args) output_file.output_ext

The output file will use the extension specified in ``convert_to``. Post-processing args
can still be set  with ``convert_with`` set to ``yt-dlp``.

format
------
Set ``--format`` to pass into yt-dlp to download a specific format quality.
Uses the same syntax as yt-dlp.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       format: "(bv*[height<=1080]+bestaudio/best[height<=1080])"

format
~~~~~~
yt-dlp format, uses same syntax as yt-dlp.

match_filters
-------------
Set ``--match-filters``` to pass into yt-dlp to filter entries from being downloaded.
Uses the same syntax as yt-dlp.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       match_filters:
         filters: "original_url!*=/shorts/"

Supports one or multiple filters:

.. code-block:: yaml

   presets:
     my_example_preset:
       match_filters:
         filters:
           - "age_limit<?18"
           - "like_count>?100"
           # Other common match-filters
           # - "original_url!*=/shorts/ & !is_live"
           # - "age_limit<?18"
           # - "availability=?public"

filters
~~~~~~~
The filters themselves. If used multiple times, the filter matches if at least one of the
conditions are met. For logical AND's between match filters, use the ``&`` operator in
a single match filter. These are applied when gathering metadata.

music_tags
----------
Adds tags to every download audio file using
`MediaFile <https://mediafile.readthedocs.io/en/latest/>`_,
the same audio file tagging package used by
`beets <https://beets.readthedocs.io/en/stable/>`_.
It supports basic tags like ``title``, ``album``, ``artist`` and ``albumartist``. You can find
a full list of tags for various file types in MediaFile's
`source code <https://github.com/beetbox/mediafile/blob/v0.9.0/mediafile.py#L1770>`_.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       music_tags:
         tags:
           artist: "{artist}"
           album: "{album}"
           # Supports id3v2.4 multi-tags
           genres:
             - "{genre}"
             - "ytdl-sub"
           albumartists:
             - "{artist}"
             - "ytdl-sub"

embed_thumbnail
~~~~~~~~~~~~~~~
Optional. Whether to embed the thumbnail into the audio file.

tags
~~~~
Key, values of tag names, tag values. Supports source and override variables.
Supports lists which will get written to MP3s as id3v2.4 multi-tags.

nfo_tags
--------
Adds an NFO file for every download file. An NFO file is simply an XML file
with a ``.nfo`` extension. You can add any values into the NFO.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       nfo_tags:
         # required
         nfo_name: "{title_sanitized}.nfo"
         nfo_root: "episodedetails"
         tags:
           title: "{title}"
           season: "{upload_year}"
           episode: "{upload_month}{upload_day_padded}"
         # optional
         kodi_safe: False

kodi_safe
~~~~~~~~~
Optional. Kodi does not support > 3-byte unicode characters, which include emojis and some
foreign language characters. Setting this to True will replace those characters with '□'.
Defaults to False.

nfo_name
~~~~~~~~
The NFO file name.

nfo_root
~~~~~~~~
The root tag of the NFO's XML. In the usage above, it would look like

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
   <episodedetails>
   </episodedetails>

tags
~~~~
Tags within the nfo_root tag. In the usage above, it would look like

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
   <episodedetails>
     <title>Awesome Youtube Video</title>
     <season>2022</season>
     <episode>502</episode>
   </episodedetails>

Also supports xml attributes and duplicate keys:

.. code-block:: yaml

   tags:
     season:
       attributes:
         name: "Best Year"
       tag: "{upload_year}"
     genre:
       - "Comedy"
       - "Drama"

Which translates to

.. code-block:: xml

   <season name="Best Year">2022</season>
   <genre>Comedy</genre>
   <genre>Drama</genre>

output_directory_nfo_tags
-------------------------
Adds a single NFO file in the output directory. An NFO file is simply an XML file with a
``.nfo`` extension. It uses the last entry's source variables which can change per download
invocation. Be cautious of which variables you use.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       output_directory_nfo_tags:
         # required
         nfo_name: "tvshow.nfo"
         nfo_root: "tvshow"
         tags:
           title: "Sweet youtube TV show"
         # optional
         kodi_safe: False

kodi_safe
~~~~~~~~~
Optional. Kodi does not support > 3-byte unicode characters, which include emojis and some
foreign language characters. Setting this to True will replace those characters with '□'.
Defaults to False.

nfo_name
~~~~~~~~
The NFO file name.

nfo_root
~~~~~~~~
The root tag of the NFO's XML. In the usage above, it would look like

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
   <tvshow>
   </tvshow>

tags
~~~~
Tags within the nfo_root tag. In the usage above, it would look like

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
   <tvshow>
     <title>Sweet youtube TV show</title>
   </tvshow>

Also supports xml attributes and duplicate keys:

.. code-block:: yaml

   tags:
     named_season:
       - tag: "{source_title}"
         attributes:
           number: "{collection_index}"
     genre:
       - "Comedy"
       - "Drama"

Which translates to

.. code-block:: xml

   <title year="2022">Sweet youtube TV show</season>
   <genre>Comedy</genre>
   <genre>Drama</genre>

output_options
--------------
Defines where to output files and thumbnails after all post-processing has completed.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       output_options:
         # required
         output_directory: "/path/to/videos_or_music"
         file_name: "{title_sanitized}.{ext}"
         # optional
         thumbnail_name: "{title_sanitized}.{thumbnail_ext}"
         info_json_name: "{title_sanitized}.{info_json_ext}"
         download_archive_name: ".ytdl-sub-{subscription_name}-download-archive.json"
         migrated_download_archive_name: ".ytdl-sub-{subscription_name_sanitized}-download-archive.json"
         maintain_download_archive: True
         keep_files_before: now
         keep_files_after: 19000101

download_archive_name
~~~~~~~~~~~~~~~~~~~~~
Optional. The file name to store a subscriptions download archive placed relative to
the output directory. Defaults to ``.ytdl-sub-{subscription_name}-download-archive.json``

file_name
~~~~~~~~~
Required. The file name for the media file. This can include directories such as
``"Season {upload_year}/{title}.{ext}"``, and will be placed in the output directory.

info_json_name
~~~~~~~~~~~~~~
Optional. The file name for the media's info json file. This can include directories such
as ``"Season {upload_year}/{title}.{info_json_ext}"``, and will be placed in the output
directory. Can be set to empty string or `null` to disable info json writes.

keep_files_after
~~~~~~~~~~~~~~~~
Optional. Requires ``maintain_download_archive`` set to True.

Only keeps files that are uploaded after this datetime. By default, ytdl-sub will keep
files after ``19000101``, which implies all files. Can be used in conjunction with
``keep_max_files``.

keep_files_before
~~~~~~~~~~~~~~~~~
Optional. Requires ``maintain_download_archive`` set to True.

Only keeps files that are uploaded before this datetime. By default, ytdl-sub will keep
files before ``now``, which implies all files. Can be used in conjunction with
``keep_max_files``.

keep_max_files
~~~~~~~~~~~~~~
Optional. Requires ``maintain_download_archive`` set to True.

Only keeps N most recently uploaded videos. If set to <= 0, ``keep_max_files`` will not be
applied. Can be used in conjunction with ``keep_files_before`` and ``keep_files_after``.

maintain_download_archive
~~~~~~~~~~~~~~~~~~~~~~~~~
Optional. Maintains a download archive file in the output directory for a subscription.
It is named ``.ytdl-sub-{subscription_name}-download-archive.json``, stored in the
output directory.

The download archive contains a mapping of ytdl IDs to downloaded files. This is used to
create a ytdl download-archive file when invoking a download on a subscription. This will
prevent ytdl from redownloading media already downloaded.

Defaults to False.

migrated_download_archive_name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Optional. Intended to be used if you are migrating a subscription with either a new
subscription name or output directory. It will try to load the archive file using this name
first, and fallback to ``download_archive_name``. It will always save to this file
and remove the original ``download_archive_name``.

output_directory
~~~~~~~~~~~~~~~~
Required. The output directory to store all media files downloaded.

thumbnail_name
~~~~~~~~~~~~~~
Optional. The file name for the media's thumbnail image. This can include directories such
as ``"Season {upload_year}/{title}.{thumbnail_ext}"``, and will be placed in the output
directory. Can be set to empty string or `null` to disable thumbnail writes.

overrides
---------
Optional. This section allows you to define variables that can be used in any string formatter.
For example, if you want your file and thumbnail files to match without copy-pasting a large
format string, you can define something like:

.. code-block:: yaml

   presets:
     my_example_preset:
       overrides:
         output_directory: "/path/to/media"
         custom_file_name: "{upload_date_standardized}.{title_sanitized}"

       # Then use the override variables in the output options
       output_options:
         output_directory: "{output_directory}"
         file_name: "{custom_file_name}.{ext}"
         thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

Override variables can contain explicit values and other variables, including both override
and source variables.

In addition, any override variable defined will automatically create a ``sanitized`` variable
for use. In the example above, ``output_directory_sanitized`` will exist and perform
sanitization on the value when used.

regex
-----
Performs regex matching on an entry's source or override variables. Regex can be used to filter
entries from proceeding with download or capture groups to create new source variables.

NOTE that YAML differentiates between single-quote (``'``) and double-quote (``"``), which can
affect regex. Double-quote implies string literals, i.e. ``"\n"`` is the literal chars ``\n``,
whereas single-quote, ``'\n'`` gets evaluated to a new line. To escape ``\`` when using
single-quote, use ``\\``. This is necessary if you want your regex to be something like
``\d\n`` to match a number and adjacent new-line. It must be written as ``\\d\n``.

If you want to regex-search multiple source variables to create a logical OR effect, you can
create an override variable that contains the concatenation of them, and search that with regex.
For example, creating the override variable ``"title_and_description": "{title} {description}"``
and using ``title_and_description`` can regex match/exclude from either ``title`` or
``description``.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       regex:
         # By default, if any match fails and has no defaults, the entry will
         # be skipped. If False, ytdl-sub will error and stop all downloads
         # from proceeding.
         skip_if_match_fails: True

         from:
           # For each entry's `title` value...
           title:
             # Perform this regex match on it to act as a filter.
             # This will only download videos with "[Official Video]" in it. Note that we
             # double backslash to make YAML happy
             match:
               - '\\[Official Video\\]'

           # For each entry's `description` value...
           description:
             # Match with capture groups and defaults.
             # This tries to scrape a date from the description and produce new
             # source variables
             match:
               - '([0-9]{4})-([0-9]{2})-([0-9]{2})'
             # Exclude any entry where the description contains #short
             exclude:
               - '#short'

             # Each capture group creates these new source variables, respectively,
             # as well a sanitized version, i.e. `captured_upload_year_sanitized`
             capture_group_names:
               - "captured_upload_year"
               - "captured_upload_month"
               - "captured_upload_day"

             # And if the string does not match, use these as respective default
             # values for the new source variables.
             capture_group_defaults:
               - "{upload_year}"
               - "{upload_month}"
               - "{upload_day}"

skip_if_match_fails
~~~~~~~~~~~~~~~~~~~
Defaults to True. If True, when any match fails and has no defaults, the entry will be
skipped. If False, ytdl-sub will error and all downloads will not proceed.

split_by_chapters
-----------------
Splits a file by chapters into multiple files. Each file becomes its own entry with the
new source variables ``chapter_title``, ``chapter_title_sanitized``, ``chapter_index``,
``chapter_index_padded``, ``chapter_count``.

If a file has no chapters, and ``when_no_chapters`` is set to "pass", then ``chapter_title`` is
set to the entry's title and ``chapter_index``, ``chapter_count`` are both set to 1.

Note that when using this plugin and performing dry-run, it assumes embedded chapters are being
used with no modifications.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       split_by_chapters:
         when_no_chapters: "pass"

when_no_chapters
~~~~~~~~~~~~~~~~
Behavior to perform when no chapters are present. Supports "pass" (continue processing),
"drop" (exclude it from output), and "error" (stop processing for everything).

subtitles
---------
Defines how to download and store subtitles. Using this plugin creates two new variables:
``lang`` and ``subtitles_ext``. ``lang`` is dynamic since you can download multiple subtitles.
It will set the respective language to the correct subtitle file.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       subtitles:
         subtitles_name: "{title_sanitized}.{lang}.{subtitles_ext}"
         subtitles_type: "srt"
         embed_subtitles: False
         languages: "en"  # supports list of multiple languages
         allow_auto_generated_subtitles: False

allow_auto_generated_subtitles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Optional. Whether to allow auto generated subtitles. Defaults to False.

embed_subtitles
~~~~~~~~~~~~~~~
Optional. Whether to embed the subtitles into the video file. Defaults to False.
NOTE: webm files can only embed "vtt" subtitle types.

languages
~~~~~~~~~
Optional. Language code(s) to download for subtitles. Supports a single or list of multiple
language codes. Defaults to "en".

subtitles_name
~~~~~~~~~~~~~~
Optional. The file name for the media's subtitles if they are present. This can include
directories such as ``"Season {upload_year}/{title_sanitized}.{lang}.{subtitles_ext}"``, and
will be placed in the output directory. ``lang`` is dynamic since you can download multiple
subtitles. It will set the respective language to the correct subtitle file.

subtitles_type
~~~~~~~~~~~~~~
Optional. One of the subtitle file types "srt", "vtt", "ass", "lrc". Defaults to "srt"

throttle_protection
-------------------
Provides options to make ytdl-sub look more 'human-like' to protect from throttling. For
range-based values, a random number will be chosen within the range to avoid sleeps looking
scripted.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       throttle_protection:
         sleep_per_download_s:
           min: 2.2
           max: 10.8
         sleep_per_subscription_s:
           min: 9.0
           max: 14.1
         max_downloads_per_subscription:
           min: 10
           max: 36
         subscription_download_probability: 1.0

max_downloads_per_subscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Number of downloads to perform per subscription.

sleep_per_download_s
~~~~~~~~~~~~~~~~~~~~
Number in seconds to sleep between each download. Does not include time it takes for
ytdl-sub to perform post-processing.

sleep_per_subscription_s
~~~~~~~~~~~~~~~~~~~~~~~~
Number in seconds to sleep between each subscription.

subscription_download_probability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Probability to perform any downloads, recomputed for each subscription. This is only
recommended to set if you run ytdl-sub in a cron-job, that way you are statistically
guaranteed over time to eventually download the subscription.

video_tags
----------
Adds tags to every downloaded video file using ffmpeg ``-metadata key=value`` args.

Usage:

.. code-block:: yaml

   presets:
     my_example_preset:
       video_tags:
         title: "{title}"
         date: "{upload_date}"
         description: "{description}"

tags
~~~~
Key/values of tag names/values. Supports source and override variables.

ytdl_options
------------
Optional. This section allows you to add any ytdl argument to ytdl-sub's downloader.
The argument names can differ slightly from the command-line argument names. See
`this docstring <https://github.com/yt-dlp/yt-dlp/blob/2022.04.08/yt_dlp/YoutubeDL.py#L197>`_
for more details.

ytdl_options should be formatted like:

.. code-block:: yaml

       presets:
         my_example_preset:
           ytdl_options:
             # Ignore any download related errors and continue
             ignoreerrors: True
             # Stop downloading additional metadata/videos if it
             # exists in your download archive
             break_on_existing: True
             # Stop downloading additional metadata/videos if it
             # is out of your date range
             break_on_reject: True
             # Path to your YouTube cookies file to download 18+ restricted content
             cookiefile: "/path/to/cookies/file.txt"
             # Only download this number of videos/audio
             max_downloads: 10
             # Download and use English title/description/etc YouTube metadata
             extractor_args:
               youtube:
                 lang:
                   - "en"


where each key is a ytdl argument. Include in the example are some popular ytdl_options.
