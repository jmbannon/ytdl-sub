
Entry Variables
===============

Entry Variables
---------------

channel
~~~~~~~
The channel name if it exists, otherwise returns the uploader.

channel_id
~~~~~~~~~~
The channel id if it exists, otherwise returns the entry uploader ID.

chapters
~~~~~~~~
Chapters if they exist

comments
~~~~~~~~
Comments if they are requested

creator
~~~~~~~
The creator name if it exists, otherwise returns the channel.

description
~~~~~~~~~~~
The description if it exists. Otherwise, returns an emtpy string.

duration
~~~~~~~~
The duration of the entry in seconds

epoch
~~~~~
The unix epoch of when the metadata was scraped by yt-dlp.

epoch_date
~~~~~~~~~~
The epoch's date, in YYYYMMDD format.

epoch_hour
~~~~~~~~~~
The epoch's hour

ext
~~~
The downloaded entry's file extension

extractor
~~~~~~~~~
The yt-dlp extractor name

extractor_key
~~~~~~~~~~~~~
The yt-dlp extractor key

ie_key
~~~~~~
The ie_key, used in legacy yt-dlp things as the 'info-extractor key'

info_json_ext
~~~~~~~~~~~~~
The "info.json" extension

requested_subtitles
~~~~~~~~~~~~~~~~~~~
Subtitles if they are requested and exist

sponsorblock_chapters
~~~~~~~~~~~~~~~~~~~~~
Sponsorblock Chapters if they are requested and exist

thumbnail_ext
~~~~~~~~~~~~~
The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
need to support other image types, we always convert to jpg.

title
~~~~~
The title of the entry. If a title does not exist, returns its unique ID.

title_sanitized_plex
~~~~~~~~~~~~~~~~~~~~
The sanitized title with additional sanitizing for Plex. It replaces numbers with
fixed-width numbers so Plex does not recognize them as season or episode numbers.

uid
~~~
The entry's unique ID

uid_sanitized_plex
~~~~~~~~~~~~~~~~~~
The sanitized uid with additional sanitizing for Plex. Replaces numbers with
fixed-width numbers so Plex does not recognize them as season or episode numbers.

uploader
~~~~~~~~
The uploader if it exists, otherwise return the uploader ID.

uploader_id
~~~~~~~~~~~
The uploader id if it exists, otherwise return the unique ID.

uploader_url
~~~~~~~~~~~~
The uploader url if it exists, otherwise returns the webpage_url.

webpage_url
~~~~~~~~~~~
The url to the webpage.

Metadata Variables
------------------

entry_metadata
~~~~~~~~~~~~~~
The entry's info.json

playlist_metadata
~~~~~~~~~~~~~~~~~
Metadata from the playlist (i.e. the parent metadata, like playlist -> entry)

sibling_metadata
~~~~~~~~~~~~~~~~
Metadata from any sibling entries that reside in the same playlist as this entry.

source_metadata
~~~~~~~~~~~~~~~
Metadata from the source (i.e. the grandparent metadata, like channel -> playlist -> entry)

Playlist Variables
------------------

playlist_count
~~~~~~~~~~~~~~
Playlist count if it exists, otherwise returns ``1``.

Note that for channels/playlists, any change (i.e. adding or removing a video) will make
this value change. Use with caution.

playlist_description
~~~~~~~~~~~~~~~~~~~~
The playlist description if it exists, otherwise returns the entry's description.

playlist_index
~~~~~~~~~~~~~~
Playlist index if it exists, otherwise returns ``1``.

Note that for channels/playlists, any change (i.e. adding or removing a video) will make
this value change. Use with caution.

playlist_index_padded
~~~~~~~~~~~~~~~~~~~~~
playlist_index padded two digits

playlist_index_padded6
~~~~~~~~~~~~~~~~~~~~~~
playlist_index padded six digits.

playlist_index_reversed
~~~~~~~~~~~~~~~~~~~~~~~
Playlist index reversed via ``playlist_count - playlist_index + 1``

playlist_index_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
playlist_index_reversed padded two digits

playlist_index_reversed_padded6
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
playlist_index_reversed padded six digits.

playlist_max_upload_date
~~~~~~~~~~~~~~~~~~~~~~~~
Max upload_date for all entries in this entry's playlist if it exists, otherwise returns
``upload_date``

playlist_max_upload_year
~~~~~~~~~~~~~~~~~~~~~~~~
Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
``upload_year``

playlist_max_upload_year_truncated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The max playlist truncated upload year for all entries in this entry's playlist if it
exists, otherwise returns ``upload_year_truncated``.

playlist_title
~~~~~~~~~~~~~~
Name of its parent playlist/channel if it exists, otherwise returns its title.

playlist_uid
~~~~~~~~~~~~
The playlist unique ID if it exists, otherwise return the entry unique ID.

playlist_uploader
~~~~~~~~~~~~~~~~~
The playlist uploader if it exists, otherwise return the entry uploader.

playlist_uploader_id
~~~~~~~~~~~~~~~~~~~~
The playlist uploader id if it exists, otherwise returns the entry uploader ID.

playlist_uploader_url
~~~~~~~~~~~~~~~~~~~~~
The playlist uploader url if it exists, otherwise returns the playlist webpage_url.

playlist_webpage_url
~~~~~~~~~~~~~~~~~~~~
The playlist webpage url if it exists. Otherwise, returns the entry webpage url.

Release Date Variables
----------------------

release_date
~~~~~~~~~~~~
The entry’s release date, in YYYYMMDD format. If not present, return the upload date.

release_date_standardized
~~~~~~~~~~~~~~~~~~~~~~~~~
The release date formatted as YYYY-MM-DD

release_day
~~~~~~~~~~~
The release day as an integer (no padding).

release_day_of_year
~~~~~~~~~~~~~~~~~~~
The day of the year, i.e. February 1st returns ``32``

release_day_of_year_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~
The release day of year, but padded i.e. February 1st returns "032"

release_day_of_year_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The release day, but reversed using ``{total_days_in_year} + 1 - {release_day}``,
i.e. February 2nd would have release_day_of_year_reversed of ``365 + 1 - 32`` = ``334``

release_day_of_year_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The reversed release day of year, but padded i.e. December 31st returns "001"

release_day_padded
~~~~~~~~~~~~~~~~~~
The entry's release day padded to two digits, i.e. the fifth returns "05"

release_day_reversed
~~~~~~~~~~~~~~~~~~~~
The release day, but reversed using ``{total_days_in_month} + 1 - {release_day}``,
i.e. August 8th would have release_day_reversed of ``31 + 1 - 8`` = ``24``

release_day_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The reversed release day, but padded. i.e. August 30th returns "02".

release_month
~~~~~~~~~~~~~
The release month as an integer (no padding).

release_month_padded
~~~~~~~~~~~~~~~~~~~~
The entry's release month padded to two digits, i.e. March returns "03"

release_month_reversed
~~~~~~~~~~~~~~~~~~~~~~
The release month, but reversed
using ``13 - {release_month}``, i.e. March returns ``10``

release_month_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The reversed release month, but padded. i.e. November returns "02"

release_year
~~~~~~~~~~~~
The entry's release year

release_year_truncated
~~~~~~~~~~~~~~~~~~~~~~
The last two digits of the release year, i.e. 22 in 2022

release_year_truncated_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The release year truncated, but reversed using ``100 - {release_year_truncated}``, i.e.
2022 returns ``100 - 22`` = ``78``

Source Variables
----------------

source_count
~~~~~~~~~~~~
The source count if it exists, otherwise returns the playlist count.

source_description
~~~~~~~~~~~~~~~~~~
The source description if it exists, otherwise returns the playlist description.

source_index
~~~~~~~~~~~~
Source index if it exists, otherwise returns ``1``.

It is recommended to not use this unless you know the source will never add new content
(it is easy for this value to change).

source_index_padded
~~~~~~~~~~~~~~~~~~~
The source index, padded.

source_title
~~~~~~~~~~~~
Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
returns its playlist_title.

source_uid
~~~~~~~~~~
The source unique id if it exists, otherwise returns the playlist unique ID.

source_uploader
~~~~~~~~~~~~~~~
The source uploader if it exists, otherwise return the playlist_uploader

source_uploader_id
~~~~~~~~~~~~~~~~~~
The source uploader id if it exists, otherwise returns the playlist_uploader_id

source_uploader_url
~~~~~~~~~~~~~~~~~~~
The source uploader url if it exists, otherwise returns the source webpage_url.

source_webpage_url
~~~~~~~~~~~~~~~~~~
The source webpage url if it exists, otherwise returns the playlist webpage url.

Upload Date Variables
---------------------

upload_date
~~~~~~~~~~~
The entry’s uploaded date, in YYYYMMDD format. If not present, return today’s date.

upload_date_standardized
~~~~~~~~~~~~~~~~~~~~~~~~
The uploaded date formatted as YYYY-MM-DD

upload_day
~~~~~~~~~~
The upload day as an integer (no padding).

upload_day_of_year
~~~~~~~~~~~~~~~~~~
The day of the year, i.e. February 1st returns ``32``

upload_day_of_year_padded
~~~~~~~~~~~~~~~~~~~~~~~~~
The upload day of year, but padded i.e. February 1st returns "032"

upload_day_of_year_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``

upload_day_of_year_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The reversed upload day of year, but padded i.e. December 31st returns "001"

upload_day_padded
~~~~~~~~~~~~~~~~~
The entry's upload day padded to two digits, i.e. the fifth returns "05"

upload_day_reversed
~~~~~~~~~~~~~~~~~~~
The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``

upload_day_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~
The reversed upload day, but padded. i.e. August 30th returns "02".

upload_month
~~~~~~~~~~~~
The upload month as an integer (no padding).

upload_month_padded
~~~~~~~~~~~~~~~~~~~
The entry's upload month padded to two digits, i.e. March returns "03"

upload_month_reversed
~~~~~~~~~~~~~~~~~~~~~
The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``

upload_month_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The reversed upload month, but padded. i.e. November returns "02"

upload_year
~~~~~~~~~~~
The entry's upload year

upload_year_truncated
~~~~~~~~~~~~~~~~~~~~~
The last two digits of the upload year, i.e. 22 in 2022

upload_year_truncated_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
2022 returns ``100 - 22`` = ``78``

Ytdl-Sub Variables
------------------

download_index
~~~~~~~~~~~~~~
The i'th entry downloaded. NOTE that this is fetched dynamically from the download
archive.

download_index_padded6
~~~~~~~~~~~~~~~~~~~~~~
The download_index padded six digits

upload_date_index
~~~~~~~~~~~~~~~~~
The i'th entry downloaded with this upload date.

upload_date_index_padded
~~~~~~~~~~~~~~~~~~~~~~~~
The upload_date_index padded two digits

upload_date_index_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~
100 - upload_date_index

upload_date_index_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The upload_date_index padded two digits

ytdl_sub_input_url
~~~~~~~~~~~~~~~~~~
The input URL used in ytdl-sub to create this entry.
