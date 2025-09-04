Automating
==========

Automate downloading your subscriptions by running the :ref:`'sub' sub-command
<usage:subscriptions options>` periodically. There are various tools that can run
commands on a schedule you may use any of them that work with your installation
method. Most users use `cron`_ in `Docker containers <docker and unraid_>`_.


Docker and Unraid
-----------------

:doc:`The 'ytdl-sub' Docker container images <../install/docker>` provide optional cron
support. Enable cron support by setting `a cron schedule`_ in the ``CRON_SCHEDULE``
environment variable:

.. code-block:: yaml
  :caption: ./compose.yaml
  :emphasize-lines: 4

  services:
    ytdl-sub:
      environment:
        CRON_SCHEDULE: "0 */6 * * *"

Then recreate the container to apply the change and start it to generate the default
``/config/ytdl-sub-configs/cron`` script. Read the comments in that script and edit as
appropriate.

The container cron wrapper script will write output from the cron job to
``/config/ytdl-sub-configs/.cron.log``. The default image ``ENTRYPOINT`` will ``$ tail
...`` that file so you can monitor the cron job in the container's output and thus also
in the Docker logs.


.. _linux-setup:

Linux, Mac OS X, BSD, or other UNIX's
-------------------------------------

For installations on systems already running ``# crond``, you can also use cron to run
``ytdl-sub`` periodically. Write a script to run ``ytdl-sub`` in the cron job. Be sure
the script changes to the same directory as your configuration and uses the full path to
``ytdl-sub``:

.. code-block:: shell
   :caption: ~/.local/bin/ytdl-sub-cron
   :emphasize-lines: 2,3

   #!/bin/bash
   cd "~/.config/ytdl-sub/"
   ~/.local/bin/ytdl-sub --dry-run sub -o '--ytdl_options.max_downloads 3' |&
       tee -a "~/.local/state/ytdl-sub/.cron.log"

Then tell ``# crond`` when to run the script:

.. code-block:: console

   echo "0 */6 * * * ${HOME}/.local/bin/ytdl-sub-cron" | crontab "-"

Remove the ``--dry-run`` and ``-o ...`` CLI options from your cron script when you've
tested your configuration and you're ready to download entries unattended.


.. _windows-setup:

Windows
-------

For most Windows users, the best way to run commands periodically is `the Task
Scheduler`_:

.. attention::

   These instructions are untested. Use at your own risk. If you use them, whether they
   work or not, please let us know how it went in `a support post in Discord`_ or `a new
   GitHub issue`_.

#. Open the Task Scheduler app.

#. Click ``Create Basic Task`` at the top of the right sidebar.

#. Set all the fields as appropriate until you get to the ``Action``...

#. For the ``Action``, select ``Start a program``...

#. Click ``Browse...`` to the installed ``ytdl-sub.exe`` executable...

#. Add CLI arguments to ``Add arguments (optional):``, for example ``--dry-run sub -o
   '--ytdl_options.max_downloads 3'``...

#. Set ``Start in (optional):`` to the directory containing your configuration.

#. Finish the rest of the ``Create Basic Task`` wizard.


Next Steps
----------

At this point, ``ytdl-sub`` should run periodically and keep your subscriptions current
in your media library without your intervention. As your :doc:`subscriptions file
<./subscriptions>` grows or you discover new use cases, it becomes worth while to
simplify things by :doc:`defining your own custom presets <./first_config>`.



.. _`cron`:
   https://en.wikipedia.org/wiki/Cron
.. _`a cron schedule`:
   https://crontab.cronhub.io/

.. _`the Task Scheduler`:
   https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page
.. _`a support post in Discord`:
   https://discord.com/channels/994270357957648404/1084886228266127460
.. _`a new GitHub issue`:
   https://github.com/jmbannon/ytdl-sub/issues/new
