FAQ
===

Since ytdl-sub is relatively new to the public, there has
not been many question asked yet. We will update this as
more questions get asked.

.. contents:: Frequently Asked Questions
  :depth: 3

How do I...
-----------

...download age-restricted YouTube videos?
''''''''''''''''''''''''''''''''''''''''''
See
`ytdls recommended way <https://github.com/ytdl-org/youtube-dl#how-do-i-pass-cookies-to-youtube-dl>`_
to download your YouTube cookie, then add it to your
:ref:`ytdl options <ytdl_options>` section of your config:

.. code-block:: yaml

   ytdl_options:
     cookiefile: "/path/to/cookies/file.txt"

...automate my downloads?
'''''''''''''''''''''''''
See :ref:`automated_downloads` on how to set up ``ytdl-sub`` to run in a cron job.
