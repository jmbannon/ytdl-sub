Getting Started
===============


Prerequisite Knowledge
----------------------

Using ``ytdl-sub`` requires some technical knowledge. You must be able to:

- do `basic CLI shell navigation`_
- read and write `YAML text files`_

If you plan on using a :ref:`Docker headless image variant
<guides/install/docker:headless image>` of ``ytdl-sub``, you can:

- use ``$ nano /config/...`` to edit configuration files inside the container
- or bind mount ``/config/`` as a Docker volume and use the editor of your choice from
  the host

Soon, it's time to start configuring ``ytdl-sub``. We provide a :doc:`./quick_start`
with rigid, rote instructions on how to get a minimal configuration up and running, but
if that serves all your needs, then you're probably better off with :ref:`one of the
more user-friendly yt-dlp wrappers available <introduction:motivation>`. As a lower
level tool with no GUI, most ``ytdl-sub`` users will need to understand at least some of
how ``ytdl-sub`` works, how it "thinks". So before you start configuring ``ytdl-sub``,
`read on <architecture>`_ to learn how ``ytdl-sub`` works.

.. _`basic CLI shell navigation`:
   https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line
.. _`YAML text files`: http://thomasloven.com/blog/2018/08/YAML-For-Nonprogrammers/



Architecture
------------

For most users, ``ytdl-sub`` works as follows:

Subscriptions use presets
~~~~~~~~~~~~~~~~~~~~~~~~~

Run ``$ ytdl-sub sub`` to read :doc:`a subscription file <./subscriptions>` that defines
what subscriptions to download and place into your media library. Each subscription
selects which :doc:`presets <../../prebuilt_presets/index>` to apply. Those presets
configure how each subscription is downloaded and placed in the media library.

Presets configure plugins
~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`A preset <../../prebuilt_presets/index>` is effectively a set of plugin
configurations. Specifically, a preset consists of:

- base presets that it inherits from and extends
- plugin configurations

When a preset has multiple base presets and more than one of those base presets
configures the same keys for a plugin, the later/lower base preset overrides the plugin
key configurations of earlier/higher base presets. Similarly, when the preset configures
the same keys for a plugin that one of its base plugins configures, the preset
configuration overrides the base presets.

Plugins do the work
~~~~~~~~~~~~~~~~~~~

``ytdl-sub`` applies the plugins that the presets configure when it downloads a
subscription. :doc:`The plugins <../../config_reference/plugins>` control how to run
``yt-dlp``, which media in the subscription to download, how to collect and format
metadata for those media, how to place the resulting files into your media library, and
more.

Presets and subscriptions accept overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Presets accept override keys and values and the preset uses those overrides to modify
their plugin configurations. Similarly, individual subscriptions can supply overrides of
their presets for just that subscription.

Subscriptions are grouped by indentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most subscriptions have more in common with each other than not. Thus, defining the
presets and overrides for each subscription would result in mostly repetition and would
multiply the burden of management for the user. The more subscriptions the more work.

To avoid this redundant work, and so that the subscription configurations describe the
intent of the user, subscriptions are nested/indented under parent/ancestor keys that
define their shared configuration. To support this, ``ytdl-sub`` uses special handling
of the ancestor YAML keys above each subscription. A subscription is the most
nested/indented/descendant key that specifies the URLs for that subscription. The
ancestor keys above that subscription describe the shared presets of that subscription
and all the other descendant subscriptions under them.

Genres are also more often shared between subscriptions than not. To accommodate that
reality, the ancestor keys of subscriptions may also use :ref:`the special '= ...'
prefix to pass specific overrides
<config_reference/scripting/static_variables:subscription_indent_i>` supported by the
preset. By convention in the built-in software and media type presets, the first ``=
...`` value specifies the genre for all descendant subscriptions.

Finally, ancestor keys may use :ref:`the '... | ...' special character
<config_reference/subscription_yaml:multi keys>` to combine multiple presets and/or
genres for the descendant subscriptions beneath.

The configuration file extends pre-defined presets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users define additional presets in :doc:`their configuration file <./first_config>` that
they then use in most of their subscriptions. Most user-defined presets extend the
:doc:`../../prebuilt_presets/index` provided by ``ytdl-sub``.

Minimize the work to only what's necessary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Throttling and bans are a core problem for any web scraping tool, perhaps even more so
for ``yt-dlp``, and no good actor *wants* to be an onerous burden on a
service. Similarly, many web scraping use cases involve very large sets of data that are
too big to process as a whole for performance. It's important to narrow the amount of
data considered and minimize requests.

To these ends, most presets tell ``yt-dlp`` not to consider files before the most
recently downloaded file using :ref:`the 'break_on_existing' option
<config_reference/plugins:ytdl_options>`. Similarly, and particularly for huge channels
or playlists, most users should use either :ref:`an 'Only Recent' preset
<prebuilt_presets/helpers:only recent>` and/or :ref:`the 'Chunk Downloads' preset
<prebuilt_presets/helpers:chunk downloads>` to restrict the number of downloads
considered.


Caveats
~~~~~~~

Some of these descriptions are not technically complete. For example, a subscription may
use no preset at all and will just run ``yt-dlp`` without any customization or post
processing. The subscriptions file has special support for :ref:`overriding the presets
of all subscriptions in the file <config_reference/subscription_yaml:file preset>`. The
configuration file supports :ref:`a few special options
<config_reference/config_yaml:configuration>` that are not about defining presets. See
:doc:`the reference documentation <../../config_reference/index>` for technically
complete details, but for almost all of the use cases served by ``ytdl-sub``, the above
is accurate and representative.


Next Steps
----------

With ``ytdl-sub`` installed and the above understood, the next step is to :doc:`start
adding subscriptions <./subscriptions>`.


.. toctree::
  :hidden:

  subscriptions
  first_download
  automating_downloads
  first_config
  quick_start
