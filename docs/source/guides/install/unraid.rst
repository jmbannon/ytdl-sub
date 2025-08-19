======
Unraid
======

You can install our :unraid:`unraid community apps <community/apps?q=ytdl-sub#r>`
through the `Unraid Community Apps plugin <https://unraid.net/community/apps>`_.

If you installed the ``ytdl-sub-gui`` app, the code-server will be running at
http://localhost:8443 (replace ``localhost`` with the IP of the computer running Unraid
if you aren't trying to access ``ytdl-sub`` on that computer). Open this page in a
browser to access and interact with ``ytdl-sub``.

If you installed the ``ytdl-sub`` app (headless), open the normal app-specific console
to access and interact with ``ytdl-sub``. Once open, you must first run ``su abc -s
/bin/bash`` to change to the non-root user. You can confirm that this command worked by
running ``whoami`` and verifying that the result is ``abc``.

.. warning::

   If you use the below option to access the ``ytdl-sub`` console, be sure to run ``su
   abc -s /bin/bash`` first thing. You can confirm that this command worked by running
   ``whoami`` and verifying that the result is ``abc``. Do **NOT** run ``ytdl-sub`` as
   the root user! Running as root will set the owner of all modified files to root,
   which prevents most media managers and players from accessing the files.

   .. figure:: ../../../images/unraid_badconsole.png
     :alt:
	The Unraid community app plugin GUI, with an arrow pointing at the "Console"
	option in the dropdown after selecting ytdl-sub-gui
