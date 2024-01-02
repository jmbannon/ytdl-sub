Unraid
--------------
You can install our :unraid:`unraid community apps <community/apps?q=ytdl-sub#r>` through the  `Unraid Community Apps plugin <https://unraid.net/community/apps>`_.


After starting, if you installed the ``ytdl-sub-gui`` app, the code-server will be running at http://localhost:8443 (replace ``localhost`` with the IP of the computer running Unraid if you aren't trying to access ``ytdl-sub`` on that computer). Open this page in a browser to access and interact with ``ytdl-sub``. 

At this time, we are unsure how to access the headless ``ytdl-sub`` console using the user ``abc`` and not ``root``. If you use Unraid and can help us figure this out, please contact the code owner or join the Discord.

.. warning:: 
  Do **NOT** use the below option to access ``ytdl-sub``. Running from this option **WILL** break things.

  .. figure:: ../../../images/unraid_badconsole.png
    :alt: The Unraid community app plugin GUI, with an arrow pointing at the "Console" option in the dropdown after selecting ytdl-sub-gui