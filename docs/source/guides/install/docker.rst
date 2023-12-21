======
Docker
======

Docker Compose
--------------
.. _LSIO-based images: https://www.linuxserver.io/

The ytdl-sub Docker images use
`LSIO-based images`_
and install ytdl-sub on top. There are two flavors to choose from.

For automating ``subscriptions.yaml`` downloads to pull new media, see
:doc:`/guides/getting_started/automating_downloads` on how to set up a cron job in any of the docker containers.

GUI Image
~~~~~~~~~

The GUI image uses LSIO's
`code-server <https://hub.docker.com/r/linuxserver/code-server>`_
for its base image. More info on other code-server environment variables
can be found within its documentation. This is the recommended way to use ``ytdl-sub``.

After starting, code-server will be running at http://localhost:8443/, which is how you will access and interact with ``ytdl-sub``.

.. code-block:: yaml

  services:
  ytdl-sub:
    image: ghcr.io/jmbannon/ytdl-sub-gui:latest
    container_name: ytdl-sub
    environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Los_Angeles
    volumes:
    - <path/to/ytdl-sub/config>:/config
    - <path/to/tv_shows>:/tv_shows  # optional
    - <path/to/movies>:/movies  # optional
    - <path/to/music_videos>:/music_videos  # optional
    - <path/to/music>:/music  # optional
    ports:
    - 8443:8443
    restart: unless-stopped

Headless Image
~~~~~~~~~~~~~~

The headless image uses LSIO's
`baseimage-alpine <https://github.com/linuxserver/docker-baseimage-alpine>`_
for its base image. With this image, ``ytdl-sub`` is meant to be ran from console
via exec'ing into the image using the command:

.. code-block:: bash

  docker exec -u abc -it ytdl-sub /bin/bash

This is how you will access and interact with ``ytdl-sub``.


.. code-block:: yaml

  services:
  ytdl-sub:
    image: ghcr.io/jmbannon/ytdl-sub:latest
    container_name: ytdl-sub
    environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Los_Angeles
    - DOCKER_MODS=linuxserver/mods:universal-cron
    volumes:
    - <path/to/ytdl-sub/config>:/config
    - <path/to/tv_shows>:/tv_shows  # optional
    - <path/to/movies>:/movies  # optional
    - <path/to/music_videos>:/music_videos  # optional
    - <path/to/music>:/music  # optional
    restart: unless-stopped

CPU/GPU Passthrough
~~~~~~~~~~~~~~~~~~~
For CPU or GPU passthrough, you must use either the GUI image or the headless Ubuntu image
``ghcr.io/jmbannon/ytdl-sub:ubuntu-latest``.

The docker-compose examples use the GUI image.

CPU
^^^

.. code-block:: yaml

  services:
  ytdl-sub:
    image: ghcr.io/jmbannon/ytdl-sub-gui:latest
    container_name: ytdl-sub
    environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Los_Angeles
    volumes:
    - <path/to/ytdl-sub/config>:/config
    - <path/to/tv_shows>:/tv_shows  # optional
    - <path/to/movies>:/movies  # optional
    - <path/to/music_videos>:/music_videos  # optional
    - <path/to/music>:/music  # optional
    ports:
    - 8443:8443
    devices:
    - /dev/dri:/dev/dri  # CPU passthrough
    restart: unless-stopped

GPU
^^^

.. code-block:: yaml

  services:
  ytdl-sub:
    image: ghcr.io/jmbannon/ytdl-sub-gui:latest
    container_name: ytdl-sub
    environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Los_Angeles
    - NVIDIA_DRIVER_CAPABILITIES=all  # Nvidia ENV args
    - NVIDIA_VISIBLE_DEVICES=all
    volumes:
    - <path/to/ytdl-sub/config>:/config
    - <path/to/tv_shows>:/tv_shows  # optional
    - <path/to/movies>:/movies  # optional
    - <path/to/music_videos>:/music_videos  # optional
    - <path/to/music>:/music  # optional
    ports:
    - 8443:8443
    deploy:
    resources:
      reservations:
      devices:
        - capabilities: [gpu]  # GPU passthrough
    restart: unless-stopped

Docker CLI
----------

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
    --restart unless-stopped \
    ghcr.io/jmbannon/ytdl-sub-gui:latest