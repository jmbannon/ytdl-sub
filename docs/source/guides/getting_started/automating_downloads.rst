Automating Downloads
====================

One of the key capabilities of ``ytdl-sub`` is how well it runs without user input, but to take advantage of this you must set up scheduling to execute the commands at some interval. How you set up this scheduling depends on which version of ``ytdl-sub`` you downloaded.


:ref:`Guide for Docker and Unraid Containers <guides/getting_started/automating_downloads:docker and unraid>`

:ref:`Guide for Linux <guides/getting_started/automating_downloads:linux>`

:ref:`Guide for Windows <guides/getting_started/automating_downloads:windows>`

.. _cron tab manpage: https://man7.org/linux/man-pages/man5/crontab.5.html#EXAMPLE_CRON_FILE

.. _docker-unraid-setup:

Docker and Unraid
-----------------

.. tab-set::
  
  .. tab-item:: GUI Image
    
    The script that will execute automatically is located at ``/config/run_cron``. 

    Access your container at http://localhost:8443/, then in the GUI terminal run these commands:

    .. code-block:: shell

      echo '#!/bin/bash' > /config/run_cron
      echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /config/run_cron
      echo "echo 'Cron started, running ytdl-sub...'" >> /config/run_cron
      echo "cd /config/ytdl-sub-configs" >> /config/run_cron
      echo "ytdl-sub --config=config.yaml sub subscriptions.yaml" >> /config/run_cron
      chmod +x /config/run_cron
      chown abc:abc /config/run_cron

    You can test the newly created script by running: 

    .. code-block:: shell

      /config/run_cron

    To create the cron definition, run the following command:

    .. code-block:: shell

      echo "# min   hour    day     month   weekday command" > /config/crontabs/abc
      echo "  0     */6     *       *       *       /config/run_cron" >> /config/crontabs/abc

    This will run the script every 6 hours. To run every hour, change ``*/6`` to ``*/1``, or to run once a day, change the same value to the hour (in 24hr format) that you want it to run at. See the `cron tab manpage`_ for more options.

  .. tab-item:: Headless Image

    .. _LinuxServer's Universal Cron mod: https://github.com/linuxserver/docker-mods/tree/universal-cron

    The first step is to ensure you have `LinuxServer's Universal Cron mod`_ enabled via the environment variable. For the GUI image, this is already included (no need to add it).

    .. code-block:: yaml

      services:
        ytdl-sub:
          image: ghcr.io/jmbannon/ytdl-sub:latest
          container_name: ytdl-sub
          environment:
            - PUID=1000
            - PGID=1000
            - TZ=America/Los_Angeles
            - DOCKER_MODS=linuxserver/mods:universal-cron  # <-- Make sure you have this!
          volumes:
            # ensure directories have user permissions
            - </path/to/ytdl-sub/config>:/config
            - </path/to/ytdl-sub/tv_shows>:/tv_shows
          restart: unless-stopped

    This line will tell your container to install and enable cron on start.

    If you had to add this line, you will need to restart your container.

    .. code-block:: shell

      docker compose restart

    The script that will execute automatically is located at ``/config/run_cron``. 

    Access your container from the terminal by running:

    .. code-block:: shell

      docker exec -itu abc ytdl-sub /bin/bash

    then in the terminal run these commands:

    .. code-block:: shell

      echo '#!/bin/bash' > /config/run_cron
      echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /config/run_cron
      echo "echo 'Cron started, running ytdl-sub...'" >> /config/run_cron
      echo "cd /config/ytdl-sub-configs" >> /config/run_cron
      echo "ytdl-sub --config=config.yaml sub subscriptions.yaml" >> /config/run_cron
      chmod +x /config/run_cron
      chown abc:abc /config/run_cron

    You can test the newly created script by running: 

    .. code-block:: 

      /config/run_cron

    To create the cron definition, run the following command:

    .. code-block:: shell

      echo "# min   hour    day     month   weekday command" > /config/crontabs/abc
      echo "  0     */6     *       *       *       /config/run_cron" >> /config/crontabs/abc
    
    This will run the script every 6 hours. To run every hour, change ``*/6`` to ``*/1``, or to run once a day, change the same value to the hour (in 24hr format) that you want it to run at. See the `cron tab manpage`_ for more options.

.. _linux-setup:

Linux 
-----

.. code-block:: shell

  crontab -e
  0     */6     *       *       *       /config/run_cron




.. _windows-setup:

Windows
-------
To be tested (please contact code owner or join the discord server if you can test this out for us)

.. code-block:: powershell

  ytdl-sub.exe --config \path\to\config\config.yaml sub \path\to\config\subscriptions.yaml