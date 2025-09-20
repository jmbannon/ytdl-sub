==================
Subscription File
==================

A subscription file is designed to both define and organize many things to download in
condensed YAML.

.. hint::

  Read the :ref:`getting started guide <guides/getting_started/index:Getting Started>`
  first before reviewing this section.


File Preset
-----------

Many examples show ``__preset__`` at the top. This is known as the *subscription file
preset*.  It is where a single :ref:`preset <guides/getting_started/first_config:Custom
Preset Definition>` can be defined that gets applied to each subscription within the
file.

This is a good place to apply file-wide variables such as ``tv_show_directory`` or
supply a cookies file path.

.. code-block:: yaml

  __preset__:
    # Variables that override defaults from `overrides:` for presets in YAML keys:
    overrides:
      tv_show_directory: "/tv_shows"

    # Directly set plugin options:
    ytdl_options:
      cookiefile: "/config/ytdl-sub-configs/cookie.txt"

Layout
------

A subscription file is comprised of YAML keys and values. Keys can be either

- a preset
- an override value
- a subscription name

Take the following example:

.. code-block:: yaml

  Jellyfin TV Show by Date:
    = News:
      "Breaking News": "https://www.youtube.com/@SomeBreakingNews"
      "BBC News": "https://www.youtube.com/@BBCNews"

All three types of keys are used for the following:

- ``Jellyfin TV Show by Date`` - a prebuilt preset
- ``= News`` - an override value for genre
- ``Breaking News``, ``BBC News`` - The subscription names

The lowest level, most indented keys should always be the subscription name.  It is good
practice to put subscription names in quotes to differentiate between preset names and
subscription names.

Values should always be the subscription itself. The simplest form is just the
URL. Further sections will show more exotic examples that go beyond a single URL.


Inheritance
-----------

A subscription inherits every key above it. In the above example, both ``Breaking News``
and ``BBC News`` inherits the ``Jellyfin TV Show by Date`` preset and the ``= News``
override value.

.. note::

  There are no limits or boundaries on how one structures their presets. This
  flexibility is intended for subscription authors to organize their downloads as they
  see fit.


Multi Keys
----------

Subscription keys support pipe syntax, or ``|``, which allows multiple keys to be
defined on a single line. The following is equivalent to the above example:

.. code-block:: yaml

  Jellyfin TV Show by Date | = News:
    "Breaking News": "https://www.youtube.com/@SomeBreakingNews"
    "BBC News": "https://www.youtube.com/@BBCNews"


Override Mode
-------------

Often times, it is convenient to set multiple override values for a single
subscription. We can put a preset in *override mode* by using tilda syntax, or ``~``.

Suppose we want to apply the :ref:`Only Recent <prebuilt_presets/helpers:Only Recent>`
preset to the above examples. But for ``BBC News`` specifically, we want to set the date
range to be different than the default ``2months`` value to ``2weeks``.

We can change it as follows:

.. code-block:: yaml

  Jellyfin TV Show by Date
    = News | Only Recent:
      "Breaking News": "https://www.youtube.com/@SomeBreakingNews"
      "~BBC News":
        url: "https://www.youtube.com/@BBCNews"
        only_recent_date_range: "2weeks"

.. important::

  When using override mode, we need to set the ``url`` variable since we are no longer
  using the simplified *subscription_value*. For more info on how this works, read about
  :ref:`subscription variables <config_reference/scripting/static_variables:Subscription
  Variables>`.


Map Mode
--------

Map mode is for highly advanced presets that benefit from a more complex subscription
definition. TODO: Show music video example here.
