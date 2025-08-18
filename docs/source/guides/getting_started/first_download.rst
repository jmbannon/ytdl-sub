Initial Download
================

Once you've created :doc:`a subscriptions file <./subscriptions>`, you can perform your
first download. Access ``ytdl-sub``, navigate to the directory containing your
``subscriptions.yaml`` file.


Dry Run
-------

Performing a dry run is important when applying any change to your subscriptions to
ensure output looks as expected. Dry runs will pull metadata to *simulate* a download
without actually downloading the media file.

.. code-block:: shell

  ytdl-sub --dry-run sub subscriptions.yaml


Faster Iteration Cycle
----------------------

Testing subscriptions can take quite some time to perform a full download.  This can be
speed up by applying an override via command-line to set max number of downloads.

.. code-block:: shell

  ytdl-sub --dry-run sub subscriptions.yaml -o '--ytdl_options.max_downloads 3'

Having many subscriptions could still make this dry run take a while. A subset of
subscriptions can be dry ran using a match.

.. code-block:: shell
  :caption: Only run subscriptions that have PBS in their names

  ytdl-sub --dry-run sub subscriptions.yaml -o '--ytdl_options.max_downloads 3' --match PBS


Downloading
-----------

Once the subscriptions file is validated, a download can be performed by omitting the
dry run argument.

.. code-block:: shell

  ytdl-sub sub subscriptions.yaml

Multiple subscription file names can be provided to perform a download on all of them. A
single file named ``subscriptions.yaml`` does not require a file name specification
since it will look for that file name by default, making the following command valid.

.. code-block:: shell

  ytdl-sub sub
