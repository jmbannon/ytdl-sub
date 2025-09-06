======
Docker
======

The ``ytdl-sub`` Docker images use :lsio:`LSIO-based images <\ >` and install ytdl-sub
on top. There are two flavors or variants to choose from. For a more user-friendly
experience editing the `configuration`_, we recommend the `GUI image`_
variant. :ref:`Docker Compose <guides/install/docker:install with docker compose>` is
the recommended way of managing a ``ytdl-sub`` docker container.  See :ref:`Automating
Downloads <guides/getting_started/automating_downloads:docker and unraid>` for how to
automate running ``ytdl-sub`` in a container running either variant.


GUI Image
---------

The GUI image is based on LSIO's :lsio-gh:`docker-code-server` to provide you full
management of ``ytdl-sub``, such as file editing and terminal access, all within your
browser using the VS Code web UI. See its documentation regarding environment variables
and other details. Once running, open `the web UI`_ to edit the `configuration`_ and run
``ytdl-sub``.

.. _`the web UI`: http://localhost:8443


Headless Image
--------------

The headless image is based on LSIO's :lsio-gh:`docker-baseimage-alpine`. Once running,
the default command just starts services including cron for :ref:`Automating Downloads
<guides/getting_started/automating_downloads:docker and unraid>` but otherwise doesn't
run ``ytdl-sub``. You may run arbitrary ``ytdl-sub`` commands using the
``--rm --user="${PUID}:${PGID}" --entrypoint="ytdl-sub"`` options to either ``$ docker
run`` or ``$ docker compose run``. Overriding the image's ``ENTRYPOINT`` is important so
that cron doesn't run ``ytdl-sub`` while you're running it manually.

For example::

  $ docker compose run --rm --user="${PUID}:${PGID}" --entrypoint="ytdl-sub" ytdl-sub sub

.. note::

   In `the recommended GUI image <gui image_>`_, the ``DEFAULT_WORKSPACE`` directory is
   ``/config/ytdl-sub-configs/`` which is used throughout the documentation and
   examples. In the headless images, that directory is just ``/config/``, so substitute
   that path if using a headless image.


Install with Docker Compose
---------------------------

Docker Compose provides a declarative way to configure and orchestrate containers which
makes them easier to manage and re-use. Create a ``compose.yaml`` file in your project
directory such as:

.. code-block:: yaml
   :caption: compose.yaml

   services:
     ytdl-sub:
       # The GUI image variant:
       image: ghcr.io/jmbannon/ytdl-sub-gui:latest
       # Or use the headless image variant:
       # image: ghcr.io/jmbannon/ytdl-sub:latest
       # For CPU/GPU passthrough, use the GUI image above or the headless Ubuntu image:
       # image: ghcr.io/jmbannon/ytdl-sub:ubuntu-latest
       container_name: ytdl-sub
       restart: unless-stopped
       environment:
         - TZ=America/Los_Angeles
         # Set these as appropriate so your users can access the downloaded files in
         # your library:
         - PUID=1000
         - PGID=1000
         # Optionally passthrough your NVidia GPU:
         # - NVIDIA_DRIVER_CAPABILITIES=all
         # - NVIDIA_VISIBLE_DEVICES=all
       volumes:
         - <path/to/ytdl-sub/config>:/config
         - <path/to/tv_shows>:/tv_shows  # optional
         - <path/to/movies>:/movies  # optional
         - <path/to/music_videos>:/music_videos  # optional
         - <path/to/music>:/music  # optional
       # Not necessary for the headless image variant:
       ports:
         - 8443:8443
       # Optionally passthrough the CPU for hardware acceleration:
       # devices:
       #   - /dev/dri:/dev/dri
       # Optionally passthrough the GPU:
       # deploy:
       #   resources:
       #     reservations:
       #       devices:
       #         - capabilities: ["gpu"]


Docker CLI
----------

You can run the container on an ad-hoc basis without Docker Compose using the Docker CLI
instead. It will not restart if stopped for any reason, including rebooting the
host. The following command is for the gui image:

.. code-block:: bash

  docker run -d \
    --name=ytdl-sub \
    -e PUID=1000 \
    -e PGID=1000 \
    -e TZ=America/Los_Angeles \
    -p 8443:8443 \
    -v <path/to/ytdl-sub/config>:/config \
    -v <OPTIONAL/path/to/tv_shows>:/tv_shows \
    -v <OPTIONAL/path/to/movies>:/movies \
    -v <OPTIONAL/path/to/music_videos>:/music_videos \
    -v <OPTIONAL/path/to/music>:/music \
    ghcr.io/jmbannon/ytdl-sub-gui:latest

See `the Docker reference <https://docs.docker.com/engine/reference/run/>`_ for further
details.


Configuration
-------------

In these examples, the configuration files will be at
``<path/to/ytdl-sub/config>/config.yaml`` and
``<path/to/ytdl-sub/config>/subscriptions.yaml``. Start the container the first time to
populate those files with default examples.
