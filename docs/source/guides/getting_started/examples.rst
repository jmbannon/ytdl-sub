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