Quick Start
===========

:ref:`Again <guides/getting_started/index:prerequisite knowledge>`, if the following
serves all your needs, then you're probably better off with :ref:`one of the more
user-friendly yt-dlp wrappers available <introduction:motivation>`. If you still want to
get ``ytdl-sub`` up and running quickly and without understanding, then follow these
instructions to the letter.

#. Install using :ref:`the official Docker GUI image variant <guides/install/docker:gui
   image>`.

#. Update the paths for your media library:

   Edit :ref:`the subscriptions file <guides/install/docker:configuration>`. Near the
   top, under ``__preset__:`` and then ``overrides:``, update the values under the
   ``*_directory:`` keys with the correct paths for your media library *as they appear
   inside the container*.

#. Select your media library software:

   Change the ``Plex TV Show by Date:`` *key itself* to the preset for your media
   library software. See the comment above for the available options.

#. Select the genre:

   Under the library software preset key from the previous step, change the ``=
   Documentaries`` *key itself* to the genre for this subscription prefixed with ``=
   ...``. When adding other subscriptions that have the same genre, place them under the
   same key.

#. Update the subscription name and URL:

   Under the genre key from the previous step, update the ``"NOVA PBS":`` key to the
   directory name the downloaded files should be placed beneath. This directory will be
   created under the ``tv_show_directory:`` from step #2. Then update the
   ``"https://www.youtube.com/@novapbs"`` value to the URL of the channel or playlist
   for this subscription.

#. :ref:`Preview <guides/getting_started/downloading:preview>` and :ref:`Review
   <guides/getting_started/downloading:review>` the subscription.

#. Add the rest of your subscriptions:

   Repeat steps #3-6 for each of your subscriptions. Be sure to repeat the preview and
   review steps for each subscription. In general, move slowly and carefully review
   everything. It's best to catch issues early :ref:`to avoid repeating downloads and to
   minimize requests <guides/getting_started/index:minimize the work to only what's
   necessary>`.

#. Automate downloads:

   :ref:`Set up ytdl-sub to run periodically <guides/getting_started/automating:docker
   and unraid>`.
