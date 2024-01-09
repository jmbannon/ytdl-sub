Usage
=======

.. code-block::

  ytdl-sub [GENERAL OPTIONS] {sub,dl,view} [COMMAND OPTIONS]

For Windows users, it would be ``ytdl-sub.exe``

General Options
---------------

General options must be specified before the command (i.e. ``sub``).

.. code-block:: text

  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c CONFIGPATH, --config CONFIGPATH
                        path to the config yaml, uses config.yaml if not provided
  -d, --dry-run         preview what a download would output, does not perform any video downloads or writes to output directories
  -l quiet|info|verbose|debug, --log-level quiet|info|verbose|debug
                        level of logs to print to console, defaults to info
  -t TRANSACTIONPATH, --transaction-log TRANSACTIONPATH
                        path to store the transaction log output of all files added, modified, deleted
  -st, --suppress-transaction-log
                        do not output transaction logs to console or file
  -m MATCH [MATCH ...], --match MATCH [MATCH ...]
                        match subscription names to one or more substrings, and only run those subscriptions

Sub Options
-----------
Download all subscriptions specified in each ``SUBPATH``.

.. code-block::

   ytdl-sub [GENERAL OPTIONS] sub [SUBPATH ...]

``SUBPATH`` is one or more paths to subscription files, uses ``subscriptions.yaml`` if not provided.
It will use the config specified by ``--config``, or ``config.yaml`` if not provided.

.. code-block:: text
  :caption: Additional Options

  -u, --update-with-info-json
                        update all subscriptions with the current config using info.json files
  -o DL_OVERRIDE, --dl-override DL_OVERRIDE
                        override all subscription config values using `dl` syntax, i.e. --dl-override='--ytdl_options.max_downloads 3'

Download Options
-----------------
Download a single subscription in the form of CLI arguments.

.. code-block::

  ytdl-sub [GENERAL OPTIONS] dl [SUBSCRIPTION ARGUMENTS]

``SUBSCRIPTION ARGUMENTS`` are exactly the same as YAML arguments, but use periods (``.``) instead
of indents for specifying YAML from the CLI. For example, you can represent this subscription:

.. code-block:: yaml

  rick_a:
    preset:
      - "tv_show"
    overrides:
      tv_show_name: "Rick A"
      url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"

Using the command:

.. code-block:: bash

  ytdl-sub dl \
      --preset "tv_show" \
      --overrides.tv_show_name "Rick A" \
      --overrides.url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"

See how to shorten commands using
`download aliases <https://ytdl-sub.readthedocs.io/en/latest/config_reference/config_yaml.html#ytdl_sub.config.config_validator.ConfigOptions.dl_aliases>`_.

View Options
-----------------
.. code-block::

   ytdl-sub view [-sc] [URL]

.. code-block:: text
  :caption: Additional Options

  -sc, --split-chapters
                        View source variables after splitting by chapters


Preview the source variables for a given URL. Helps when creating new configs.
