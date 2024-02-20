Initial Download
================

Once you have a ``subscriptions.yaml`` file created and filled out, you can perform your first
download. Access ``ytdl-sub``, navigate to the directory containing your ``subscriptions.yaml``
file, then run the below command:

.. tab-set:: 

  .. tab-item:: Dry run

    A dry run lets you check that your configuration doesn't throw any errors and what the expected output files of actually doing the download are, without actually downloading the full media.

    .. code-block:: shell

      ytdl-sub --dry-run sub

  .. tab-item:: Normal run

    A normal run will download all files as determined by your ``presets`` and, once processing is finished, move the downloaded and processed files to your ``output_directory``.

    .. code-block:: shell

      ytdl-sub sub

  .. tab-item:: One-time download

    Sometimes you may only want to download media once, in which case adding them to your ``subscriptions.yaml`` file is unneccessary. As an example, the below code will download the same videos as our subscription file:

    .. code-block:: shell
      
      ytdl-sub dl --preset "Jellyfin TV Show by Date" --overrides.subscription_name "NOVA PBS" --overrides.subscription_value "https://www.youtube.com/@novapbs" --overrides.tv_show_genre "Documentaries"