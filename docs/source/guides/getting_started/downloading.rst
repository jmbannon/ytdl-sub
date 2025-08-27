Downloading
===========

Once you've :doc:`defined your subscriptions <./subscriptions>`, it's time to test your
configuration and try your first download. As a web scraping tool, :ref:`it's important
to minimize the requests sent to external services
<guides/getting_started/index:minimize the work to only what's necessary>` to avoid
triggering throttling or bans. Further, a full download of even one subscription can
take significant time. Test each change to your subscriptions carefully and quickly as
follows.


Preview
-------

Preview what ``ytdl-sub`` would do for this subscription. Run the :ref:`'sub'
sub-command <usage:subscriptions options>` with CLI options to restrict requests as much
as possible:

- Pull metadata and *simulate* a download without actually downloading any media files
  using the ``--dry-run`` CLI option.

- Limit requests by narrowing the run to one subscription by giving a
  subscription name to the ``--match`` CLI option.

- Stop after just a few downloads to further minimize requests and make testing faster
  using the ``max_downloads`` setting from ``yt-dlp``.

Change to the directory containing your ``./subscriptions.yaml`` file and run with those
options:

.. code-block:: console

   cd "/config/ytdl-sub-configs/"
   ytdl-sub --dry-run --match="NOVA PBS" sub -o '--ytdl_options.max_downloads 3'

Examine the output carefully, investigate anything that doesn't look right and repeat
this step until everything looks right.


Review
------

Review the results of real downloads. Run it again without the ``--dry-run`` option to
actually download media and place the files in your library:

.. code-block:: console

   ytdl-sub --match="NOVA PBS" sub -o '--ytdl_options.max_downloads 3'

Examine the output carefully again. Then examine how the resulting downloads work in
your library. Repeat with a larger value for ``max_downloads`` and examine the output
and downloads again.


Next Steps
----------

Once you're `previewed <preview_>`_ and `reviewed <review_>`_ successful downloads of
each of your subscriptions, you're ready to run a full download of all your
subscriptions. Run the sub-command without the CLI options you used to limit what
``ytdl-sub`` does while testing:

.. code-block:: console

   ytdl-sub sub

If you're ready to let ``ytdl-sub`` run unattended, it's time to :doc:`automate
downloads <./automating_downloads>`.
