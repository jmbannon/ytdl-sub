Initial Configuration
=====================

Your first configuration will look pretty simple:

.. code-block:: yaml
  :linenos:

  configuration:
    working_directory: '.ytdl-sub-downloads'

  presets:
    "My Favorite YouTube Channels":
      preset:
        - "Jellyfin TV Show by Date"
        - "Only Recent"

      overrides:
        tv_show_directory: "/tv_shows/youtube"


The first two lines in this ``config.yaml`` file are the ``configuration``, and define the ``working_directory``, which is described near the bottom of :ref:`this section <guides/getting_started/index:quick overview of \`\`ytdl-sub\`\`>`


Line 4 begins the definition of your custom ``presets``, with line 5 being the name of your first custom ``preset``.

Lines 7 and 8 tell ``ytdl-sub`` which :doc:`/prebuilt_presets/index` to expand on; these ``presets`` already indicate that the downloaded files should be: 

- in a format usable by, and with metadata accessible to, Jellyfin
- sorted by upload date, and 
- only uploaded in the last 2 months (and will also delete any files in the media library which were uploaded over 2 months ago)

Line 11 is an override variable, ``tv_show_directory``, that tells ``ytdl-sub`` where to save your downloaded files once they've been processed, also known as the ``output_directory``. In this case, the downloaded files will be saved to the ``youtube`` folder in the root ``tv_shows`` directory.