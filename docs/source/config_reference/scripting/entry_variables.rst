
Entry Variables
===============

Entry Variables
---------------

channel
~~~~~~~
:type: ``String``
:description:
  The channel name if it exists, otherwise returns the uploader.

channel_id
~~~~~~~~~~
:type: ``String``
:description:
  The channel id if it exists, otherwise returns the entry uploader ID.

chapters
~~~~~~~~
:type: ``Array``
:description:
  Chapters if they exist

comments
~~~~~~~~
:type: ``Array``
:description:
  Comments if they are requested

creator
~~~~~~~
:type: ``String``
:description:
  The creator name if it exists, otherwise returns the channel.

description
~~~~~~~~~~~
:type: ``String``
:description:
  The description if it exists. Otherwise, returns an emtpy string.

duration
~~~~~~~~
:type: ``Integer``
:description:
  The duration of the entry in seconds if it exists. Defaults to zero otherwise.

epoch
~~~~~
:type: ``Integer``
:description:
  The unix epoch of when the metadata was scraped by yt-dlp.

epoch_date
~~~~~~~~~~
:type: ``String``
:description:
  The epoch's date, in YYYYMMDD format.

epoch_hour
~~~~~~~~~~
:type: ``String``
:description:
  The epoch's hour

ext
~~~
:type: ``String``
:description:
  The downloaded entry's file extension

extractor
~~~~~~~~~
:type: ``String``
:description:
  The yt-dlp extractor name

extractor_key
~~~~~~~~~~~~~
:type: ``String``
:description:
  The yt-dlp extractor key

ie_key
~~~~~~
:type: ``String``
:description:
  The ie_key, used in legacy yt-dlp things as the 'info-extractor key'.
  If it does not exist, return ``extractor_key``

info_json_ext
~~~~~~~~~~~~~
:type: ``String``
:description:
  The "info.json" extension

requested_subtitles
~~~~~~~~~~~~~~~~~~~
:type: ``Map``
:description:
  Subtitles if they are requested and exist

sponsorblock_chapters
~~~~~~~~~~~~~~~~~~~~~
:type: ``Array``
:description:
  Sponsorblock Chapters if they are requested and exist

thumbnail_ext
~~~~~~~~~~~~~
:type: ``String``
:description:
  The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
  need to support other image types, we always convert to jpg.

title
~~~~~
:type: ``String``
:description:
  The title of the entry. If a title does not exist, returns its unique ID.

title_sanitized_plex
~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The sanitized title with additional sanitizing for Plex. It replaces numbers with
  fixed-width numbers so Plex does not recognize them as season or episode numbers.

uid
~~~
:type: ``String``
:description:
  The entry's unique ID

uid_sanitized_plex
~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The sanitized uid with additional sanitizing for Plex. Replaces numbers with
  fixed-width numbers so Plex does not recognize them as season or episode numbers.

uploader
~~~~~~~~
:type: ``String``
:description:
  The uploader if it exists, otherwise return the uploader ID.

uploader_id
~~~~~~~~~~~
:type: ``String``
:description:
  The uploader id if it exists, otherwise return the unique ID.

uploader_url
~~~~~~~~~~~~
:type: ``String``
:description:
  The uploader url if it exists, otherwise returns the webpage_url.

webpage_url
~~~~~~~~~~~
:type: ``String``
:description:
  The url to the webpage.

----------------------------------------------------------------------------------------------------

Metadata Variables
------------------

entry_metadata
~~~~~~~~~~~~~~
:type: ``Map``
:description:
  The entry's info.json

playlist_metadata
~~~~~~~~~~~~~~~~~
:type: ``Map``
:description:
  Metadata from the playlist (i.e. the parent metadata, like playlist -> entry)

sibling_metadata
~~~~~~~~~~~~~~~~
:type: ``Array``
:description:
  Metadata from any sibling entries that reside in the same playlist as this entry.

source_metadata
~~~~~~~~~~~~~~~
:type: ``Map``
:description:
  Metadata from the source
  (i.e. the grandparent metadata, like channel -> playlist -> entry)

----------------------------------------------------------------------------------------------------

Playlist Variables
------------------

playlist_count
~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  Playlist count if it exists, otherwise returns ``1``.

  Note that for channels/playlists, any change (i.e. adding or removing a video) will make
  this value change. Use with caution.

playlist_description
~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The playlist description if it exists, otherwise returns the entry's description.

playlist_index
~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  Playlist index if it exists, otherwise returns ``1``.

  Note that for channels/playlists, any change (i.e. adding or removing a video) will make
  this value change. Use with caution.

playlist_index_padded
~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  playlist_index padded two digits

playlist_index_padded6
~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  playlist_index padded six digits.

playlist_index_reversed
~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  Playlist index reversed via ``playlist_count - playlist_index + 1``

playlist_index_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  playlist_index_reversed padded two digits

playlist_index_reversed_padded6
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  playlist_index_reversed padded six digits.

playlist_max_upload_date
~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  Max upload_date for all entries in this entry's playlist if it exists, otherwise returns
  ``upload_date``

playlist_max_upload_year
~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
  ``upload_year``

playlist_max_upload_year_truncated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The max playlist truncated upload year for all entries in this entry's playlist if it
  exists, otherwise returns ``upload_year_truncated``.

playlist_title
~~~~~~~~~~~~~~
:type: ``String``
:description:
  Name of its parent playlist/channel if it exists, otherwise returns its title.

playlist_uid
~~~~~~~~~~~~
:type: ``String``
:description:
  The playlist unique ID if it exists, otherwise return the entry unique ID.

playlist_uploader
~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The playlist uploader if it exists, otherwise return the entry uploader.

playlist_uploader_id
~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The playlist uploader id if it exists, otherwise returns the entry uploader ID.

playlist_uploader_url
~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The playlist uploader url if it exists, otherwise returns the playlist webpage_url.

playlist_webpage_url
~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The playlist webpage url if it exists. Otherwise, returns the entry webpage url.

----------------------------------------------------------------------------------------------------

Release Date Variables
----------------------

release_date
~~~~~~~~~~~~
:type: ``String``
:description:
  The entry’s release date, in YYYYMMDD format. If not present, return the upload date.

release_date_standardized
~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The uploaded date formatted as YYYY-MM-DD

release_day
~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload day as an integer (no padding).

release_day_of_year
~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The day of the year, i.e. February 1st returns ``32``

release_day_of_year_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The upload day of year, but padded i.e. February 1st returns "032"

release_day_of_year_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload day, but reversed using ``{total_days_in_year} + 1 - {release_day}``,
  i.e. February 2nd would have release_day_of_year_reversed of ``365 + 1 - 32`` = ``334``

release_day_of_year_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The reversed upload day of year, but padded i.e. December 31st returns "001"

release_day_padded
~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The entry's upload day padded to two digits, i.e. the fifth returns "05"

release_day_reversed
~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload day, but reversed using ``{total_days_in_month} + 1 - {release_day}``,
  i.e. August 8th would have release_day_reversed of ``31 + 1 - 8`` = ``24``

release_day_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The reversed upload day, but padded. i.e. August 30th returns "02".

release_month
~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload month as an integer (no padding).

release_month_padded
~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The entry's upload month padded to two digits, i.e. March returns "03"

release_month_reversed
~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload month, but reversed using ``13 - {release_month}``, i.e. March returns ``10``

release_month_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The reversed upload month, but padded. i.e. November returns "02"

release_year
~~~~~~~~~~~~
:type: ``Integer``
:description:
  The entry's upload year

release_year_truncated
~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The last two digits of the upload year, i.e. 22 in 2022

release_year_truncated_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload year truncated, but reversed using ``100 - {release_year_truncated}``, i.e.
  2022 returns ``100 - 22`` = ``78``

----------------------------------------------------------------------------------------------------

Source Variables
----------------

source_count
~~~~~~~~~~~~
:type: ``Integer``
:description:
  The source count if it exists, otherwise returns ``1``.

source_description
~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The source description if it exists, otherwise returns the playlist description.

source_index
~~~~~~~~~~~~
:type: ``Integer``
:description:
  Source index if it exists, otherwise returns ``1``.

  It is recommended to not use this unless you know the source will never add new content
  (it is easy for this value to change).

source_index_padded
~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The source index, padded two digits.

source_title
~~~~~~~~~~~~
:type: ``String``
:description:
  Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
  returns its playlist_title.

source_uid
~~~~~~~~~~
:type: ``String``
:description:
  The source unique id if it exists, otherwise returns the playlist unique ID.

source_uploader
~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The source uploader if it exists, otherwise return the playlist_uploader

source_uploader_id
~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The source uploader id if it exists, otherwise returns the playlist_uploader_id

source_uploader_url
~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The source uploader url if it exists, otherwise returns the source webpage_url.

source_webpage_url
~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The source webpage url if it exists, otherwise returns the playlist webpage url.

----------------------------------------------------------------------------------------------------

Upload Date Variables
---------------------

upload_date
~~~~~~~~~~~
:type: ``String``
:description:
  The entry’s uploaded date, in YYYYMMDD format. If not present, return today’s date.

upload_date_standardized
~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The uploaded date formatted as YYYY-MM-DD

upload_day
~~~~~~~~~~
:type: ``Integer``
:description:
  The upload day as an integer (no padding).

upload_day_of_year
~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The day of the year, i.e. February 1st returns ``32``

upload_day_of_year_padded
~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The upload day of year, but padded i.e. February 1st returns "032"

upload_day_of_year_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
  i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``

upload_day_of_year_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The reversed upload day of year, but padded i.e. December 31st returns "001"

upload_day_padded
~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The entry's upload day padded to two digits, i.e. the fifth returns "05"

upload_day_reversed
~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
  i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``

upload_day_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The reversed upload day, but padded. i.e. August 30th returns "02".

upload_month
~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload month as an integer (no padding).

upload_month_padded
~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The entry's upload month padded to two digits, i.e. March returns "03"

upload_month_reversed
~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``

upload_month_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The reversed upload month, but padded. i.e. November returns "02"

upload_year
~~~~~~~~~~~
:type: ``Integer``
:description:
  The entry's upload year

upload_year_truncated
~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The last two digits of the upload year, i.e. 22 in 2022

upload_year_truncated_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
  2022 returns ``100 - 22`` = ``78``

----------------------------------------------------------------------------------------------------

Ytdl-Sub Variables
------------------

download_index
~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The i'th entry downloaded. NOTE that this is fetched dynamically from the download
  archive.

download_index_padded6
~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The download_index padded six digits

upload_date_index
~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The i'th entry downloaded with this upload date.

upload_date_index_padded
~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The upload_date_index padded two digits

upload_date_index_reversed
~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  100 - upload_date_index

upload_date_index_reversed_padded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The upload_date_index padded two digits

ytdl_sub_input_url
~~~~~~~~~~~~~~~~~~
:type: ``String``
:description:
  The input URL used in ytdl-sub to create this entry.

ytdl_sub_input_url_count
~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The total number of input URLs as defined in the subscription.

ytdl_sub_input_url_index
~~~~~~~~~~~~~~~~~~~~~~~~
:type: ``Integer``
:description:
  The index of the input URL as defined in the subscription, top-most being the 0th index.
