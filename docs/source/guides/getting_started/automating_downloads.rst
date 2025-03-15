Automating Downloads
====================

:ref:`Guide for Docker and Unraid Containers <guides/getting_started/automating_downloads:docker and unraid>`

:ref:`Guide for Linux <guides/getting_started/automating_downloads:linux>`

:ref:`Guide for Windows <guides/getting_started/automating_downloads:windows>`

.. _cron scheduling syntax: https://crontab.guru/#0_*/6_*_*_*

.. _docker-unraid-setup:

Docker and Unraid
-----------------

Cron is preconfigured in every ytdl-sub docker container. Enable by adding the following
ENV variables to your docker setup.

.. code-block:: yaml

  services:
    ytdl-sub:
      environment:
      - CRON_SCHEDULE="0 */6 * * *"
      - CRON_RUN_ON_START=false


- ``CRON_SCHEDULE`` follows the standard `cron scheduling syntax`_. The above value will run the script once every 6 hours.
- ``CRON_RUN_ON_START`` toggles whether to run your cron script on container start.

The cron script will reside in the main directory with the file name ``cron``.
Cron logs should show when viewing the Docker logs.


.. _linux-setup:

Linux 
-----
Must configure crontab manually, like so:

.. code-block:: shell

  crontab -e
  0     */6     *       *       *       /config/run_cron




.. _windows-setup:

Windows
-------
To be tested (please contact code owner or join the discord server if you can test this out for us)

.. code-block:: powershell

  ytdl-sub.exe --config \path\to\config\config.yaml sub \path\to\config\subscriptions.yaml
