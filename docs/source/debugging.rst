Debugging
=========

Run with the ``--log-level verbose`` CLI option to see more information in the output,
such as all ``yt-dlp`` logs. Run with ``--log-level debug`` to show all log messages,
often too much information for normal operation but useful when investigating a specific
problem.

:ref:`ytdl-sub builds on yt-dlp <introduction:motivation>`, which is in itself a complex
tool. It performs an intricate and fragile task, web scraping, which in turn :ref:`is
subject to the whims of external services <guides/getting_started/index:minimize the
work to only what's necessary>` outside its control. Finally, because :ref:`ytdl-sub is
a lower-level tool <guides/getting_started/index:prerequisite knowledge>`, many users,
if not most, will have problems getting their configuration working and it can be
difficult to determine when the root cause is their configuration, just a limit imposed
by the services, or, least likely, a bug in one of the tools involved.

To expedite resolution and conserve the limited resources of both yourself and
volunteers, do as much investigation yourself as you can:

#. Start by assuming the issue is your configuration:

   Review :doc:`the guides <./guides/index>` to confirm your understanding. Increase
   output using the ``--log-level`` CLI option and read the output carefully for hints
   and clues. Use those clues to `search the docs`_. Read :doc:`the reference docs
   <./config_reference/index>` of the involved ``ytdl-sub`` components.

#. Try to determine if the issue is happening in ``yt-dlp`` or ``ytdl-sub``:

   The user's configuration tells ``ytdl-sub`` how to run ``yt-dlp``. ``yt-dlp`` handles
   all the web scraping and downloading. ``ytdl-sub`` then assembles the files and metadata
   produced by ``yt-dlp`` and places them in your library.

   If the issue is happening while scraping or downloading from the external service,
   then it's happening in the running of ``yt-dlp``. Look for output showing failed
   downloads, ``403`` errors, or signs of throttles. That doesn't mean it's a bug in
   ``yt-dlp``, it could be in how your configuration tells ``ytdl-sub`` to run
   ``yt-dlp`` or limits imposed by the service that are constantly changing, but you may
   be able to find answers from other ``yt-dlp`` users running into similar issues.

   See `the yt-dlp known issues`_ and `search their issues`_ for clues and hints. Read
   the comments for more understanding, workarounds, and maybe even fixes. If you still
   don't understand the cause after reading everything you can find there, try to find
   help in `the yt-dlp Discord`_.

#. If the issue is happening in ``ytdl-sub``, reach out for help:

   Once you've done everything you can to get your configuration working and you've
   determined that the issue isn't happening in ``yt-dlp``, look for answers in
   ``ytdl-sub``:

   #. Cut your configuration and subscriptions down to the minimum that reproduces the
      issue.

   #. Run with the ``--log-level debug`` CLI option and copy the full output.

   #. `Search the ytdl-sub issues`_ using clues and hints from the output.

   #. `Open a support post in Discord`_ with those details and all other relevant
      details.

   #. If someone from the Discord discussion directs you to, then `open a new issue`_
      with those same details.


.. _`the yt-dlp known issues`:
   https://github.com/yt-dlp/yt-dlp/wiki/FAQ#known-issues
.. _`search their issues`:
   https://github.com/yt-dlp/yt-dlp/issues
.. _`the yt-dlp Discord`:
   https://discord.gg/H5MNcFW63r

.. _`search the docs`:
   https://ytdl-sub.readthedocs.io/en/latest/search.html
.. _`search the ytdl-sub issues`:
   https://github.com/jmbannon/ytdl-sub/issues
.. _`open a support post in Discord`:
   https://discord.com/channels/994270357957648404/1084886228266127460
.. _`open a new issue`:
   https://github.com/jmbannon/ytdl-sub/issues/new
