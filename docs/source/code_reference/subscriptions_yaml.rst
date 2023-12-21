==================
Subscriptions File
==================
------------------
subscriptions.yaml
------------------

The ``subscriptions.yaml`` file is where we use our :ref:`code_reference/config_yaml:presets` in the :ref:`code_reference/config_yaml:config.yaml`
to define a ``subscription``: something we want to recurrently download such as a specific
channel or playlist.

The only difference between a ``subscription`` and ``preset`` is that the subscription
must have all required fields and ``{override_variables}`` defined so it can perform a download.

Below is an example that downloads a YouTube playlist:

.. code-block:: yaml
  :caption: config.yaml

  presets:
    playlist_preset_ex:
      download:
        download_strategy: "url"
        url: "{url}"
      output_options:
        output_directory: "{output_directory}/{playlist_name}"
        file_name: "{playlist_name}.{title}.{ext}"
      overrides:
        output_directory: "/path/to/ytdl-sub-videos"

.. code-block:: yaml
  :caption: subscription.yaml

  my_subscription_name:
    preset: "playlist_preset_ex"
    overrides:
      playlist_name: "diy-playlist"
      url: "https://youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"

Our preset ``playlist_preset_ex`` defines three
custom variables: ``{output_directory}``, ``{playlist_name}``, and ``{url}``. The subscription sets
the ``parent preset`` to ``playlist_preset_ex``, and must define the variables ``{playlist_name}``
and ``{url}`` since the preset did not.

Beautifying Subscriptions
~~~~~~~~~~~~~~~~~~~~~~~~~
Subscriptions support using presets as keys, and using keys to set override variables as values.
For example:

.. code-block:: yaml
  :caption: subscription.yaml

  TV Show Full Archive:
    = News:
        "Breaking News": "https://www.youtube.com/@SomeBreakingNews"

  TV Show Only Recent:
    = Tech | TV-Y:
      "Two Minute Papers": "https://www.youtube.com/@TwoMinutePapers"

Will create two subscriptions named "Breaking News" and "Two Minute Papers", equivalent to:

.. code-block:: yaml

  "Breaking News":
    preset:
      - "TV Show Full Archive"

    overrides:
      subscription_indent_1: "News"
      subscription_name: "Breaking News"
      subscription_value: "https://www.youtube.com/@SomeBreakingNews"

  "Two Minute Papers":
    preset:
      - "TV Show Only Recent"

    overrides:
      subscription_indent_1: "Tech"
      subscription_indent_2: "TV-Y"
      subscription_name: "Two Minute Papers"
      subscription_value: "https://www.youtube.com/@TwoMinutePapers"

You can provide as many parent presets in the form of ``keys``, and subscription indents as ``= keys``.
This can drastically simplify subscription definitions by setting things like so in your
parent preset:

.. code-block:: yaml

  presets:
    "TV Show Preset":
      overrides:
        subscription_indent_1: "default-genre"
        subscription_indent_2: "default-content-rating"

        tv_show_name: "{subscription_name}"
        url: "{subscription_value}"
        genre: "{subscription_indent_1}"
        content_rating: "{subscription_indent_2}"

.. _subscription value:

File Preset
~~~~~~~~~~~
NOTE: This is deprecated in favor of using the method in :ref:`code_reference/subscriptions_yaml:beautifying subscriptions`.

You can apply a preset to all subscriptions in the ``subscription.yaml`` file
by using the file-wide ``__preset__``:

.. code-block:: yaml
  :caption: subscription.yaml

  __preset__:
    preset: "playlist_preset_ex"

  my_subscription_name:
    overrides:
      url: "https://youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
      playlist_name: "diy-playlist"

This ``subscription.yaml`` is equivalent to the one above it because all
subscriptions automatically set ``__preset__`` as a ``parent preset``.


Subscription Value
~~~~~~~~~~~~~~~~~~~
NOTE: This is deprecated in favor of using the method in :ref:`code_reference/subscriptions_yaml:beautifying subscriptions`.

With a clever config and use of ``__preset__``, your subscriptions can typically boil
down to a name and url. You can set ``__value__`` to the name of an override variable,
and use the override variable ``subscription_name`` to achieve one-liner subscriptions.
Using the example above, we can do:

.. code-block:: yaml
  :caption: subscription.yaml

  __preset__:
    preset:
      - "tv_show"
    overrides:
      tv_show_name: "{subscription_name}"

  __value__: "url"

  # single-line subscription, sets "Brandon Acker" and the subscription value
  # to the override variables tv_show_name and url
  "Brandon Acker": "https://www.youtube.com/@brandonacker"

Traditional subscriptions that can override presets will still work when using ``__value__``.
``__value__`` can also be set within a :ref:`code_reference/config_yaml:config.yaml`.