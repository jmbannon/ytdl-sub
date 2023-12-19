=======
Plugins
=======
Plugins are used to perform any type of post-processing to the already downloaded files.

audio_extract
'''''''''''''
.. autoclass:: ytdl_sub.plugins.audio_extract.AudioExtractOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

chapters
''''''''
.. autoclass:: ytdl_sub.plugins.chapters.ChaptersOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

date_range
''''''''''
.. autoclass:: ytdl_sub.plugins.date_range.DateRangeOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

embed_thumbnail
''''''''''''''''

.. autoclass:: ytdl_sub.plugins.embed_thumbnail.EmbedThumbnailOptions()

-------------------------------------------------------------------------------

file_convert
''''''''''''
.. autoclass:: ytdl_sub.plugins.file_convert.FileConvertOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

format
''''''
.. autoclass:: ytdl_sub.plugins.format.FormatOptions()

-------------------------------------------------------------------------------

match_filters
'''''''''''''
.. autoclass:: ytdl_sub.plugins.match_filters.MatchFiltersOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

music_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.music_tags.MusicTagsOptions()

-------------------------------------------------------------------------------

nfo_tags
''''''''
.. autoclass:: ytdl_sub.plugins.nfo_tags.NfoTagsOptions()
  :members: nfo_name, nfo_root, tags, kodi_safe
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

output_directory_nfo_tags
'''''''''''''''''''''''''
.. autoclass:: ytdl_sub.plugins.output_directory_nfo_tags.OutputDirectoryNfoTagsOptions()
  :members: nfo_name, nfo_root, tags, kodi_safe
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

regex
'''''
.. autoclass:: ytdl_sub.plugins.regex.RegexOptions()
  :members: skip_if_match_fails

.. autoclass:: ytdl_sub.plugins.regex.VariableRegex()
  :members: match, capture_group_names, capture_group_defaults, exclude
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

split_by_chapters
'''''''''''''''''
.. autoclass:: ytdl_sub.plugins.split_by_chapters.SplitByChaptersOptions()
  :members: when_no_chapters
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

subtitles
'''''''''
.. autoclass:: ytdl_sub.plugins.subtitles.SubtitleOptions()
  :members: subtitles_name, subtitles_type, embed_subtitles, languages, allow_auto_generated_subtitles
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

throttle_protection
'''''''''''''''''''
.. autoclass:: ytdl_sub.plugins.throttle_protection.ThrottleProtectionOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

video_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.video_tags.VideoTagsOptions()