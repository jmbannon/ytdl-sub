Getting Started
===============

Walk-through Guide
-------------------
If you haven't read it yet, it's highly recommended to go through our
`walk-through guide <https://github.com/jmbannon/ytdl-sub/wiki/1.-Introduction>`_
to get familiar with how ``ytdl-sub`` works.

Example Configs
---------------
If you are ready to start downloading, see our
`examples directory <https://github.com/jmbannon/ytdl-sub/tree/master/examples>`_
for ready-to-use configs and subscriptions. Read through them carefully before use.

Using Example Configs
^^^^^^^^^^^^^^^^^^^^^^
Copy and paste the examples into local yaml files, modify the
``working_directory`` and ``output_directory`` with your desired paths,
and perform a dry-run using

.. code-block:: bash

   ytdl-sub \
     --dry-run \
     --config path/to/config.yaml \
     sub path/to/subscriptions.yaml

This will simulate what a download will look like.
