=========
Scripting
=========

``ytdl-sub`` fields (file-names, tags, etc) are defined using variables and scripts. The
links below contain reference documentation for each built-in variable and scripting
function.

.. toctree::
  :maxdepth: 1

  entry_variables
  static_variables
  scripting_functions
  scripting_types


How it Works
------------

Fields in the config that support ``formatters`` mean they support scripting, and will
*format* the field using its defined script.

In its most basic form, a script is a string comprised of variables and/or functions.

Static String
~~~~~~~~~~~~~

The following example sets ``ytdl-sub``'s output directory. It is
considered *static* because it does not depend on anything from an entry.

.. code-block:: yaml

   output_options:
     output_directory: "/path/to/tv_shows/Custom YTDL-SUB TV Show"

Static Variables
~~~~~~~~~~~~~~~~

``ytdl-sub`` offers a few built-in static variables, including ``subscription_name``.
We can use this instead of hard-coding it above:

.. code-block:: yaml

   output_options:
     output_directory: "/path/to/tv_shows/{subscription_name}"

The syntax for variable usage is curly-braces with the variable name within it. Assuming
our subscription is actually named "Custom YTDL-SUB TV Show", then ``ytdl-sub`` will
actually write to that directory.

Entry Variables
~~~~~~~~~~~~~~~

For context, an *entry* is a video or audio file downloaded from ``yt-dlp``.  *Entry
variables* are variables that are derived from an entry's ``info.json`` file. This file
comes from ``yt-dlp`` and contains every piece of metadata that it scraped.

These variables are not considered static since they change per entry download. There
are a few fields in ``ytdl-sub`` (i.e. ``output_directory``) that must be static. For
others, we are free to use values that derive from an entry.

Suppose we want to customize the name of an entry's output file and thumbnail to include
its title in its name. We can do that using entry variables:

.. code-block:: yaml

   output_options:
     output_directory: "/path/to/tv_shows/{subscription_name}"
     file_name: "{title}.{ext}"
     thumbnail_name: "{title}.{thumbnail_ext}"

Creating Custom Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we want to include the date in our file names. This means we'd need to update
both the ``file_name`` and ``thumbnail_name`` fields to include it.

Instead, we can create a custom *override variable*. This is ``ytdl-sub``'s method for
creating and overriding custom variables.

These are created in the ``overrides`` section. Let's take our above example and create
a ``custom_file_name`` variable to use for the entry file and thumbnail fields:

.. code-block:: yaml

   output_options:
     output_directory: "/path/to/tv_shows/{subscription_name}"
     file_name: "{custom_file_name}.{ext}"
     thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

   overrides:
     custom_file_name: "{upload_date_standardized} {title}"

Sanitizing Variables
~~~~~~~~~~~~~~~~~~~~

For experienced ``yt-dlp`` scrapers, you may be thinking:

- What if the title has characters that do not play nice with my operating system?

``ytdl-sub`` is able to *sanitize* any variable, meaning it replaces any problematic
characters with safe alternatives that can be used in file names. We can ensure our file
names and directories are safe by using:

.. code-block:: yaml

   output_options:
     output_directory: "/path/to/tv_shows/{subscription_name_sanitized}"
     file_name: "{custom_file_name}.{ext}"
     thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

   overrides:
     custom_file_name: "{upload_date_standardized} {title_sanitized}"

Simply add a ``_sanitized`` suffix to any variable name to make it sanitized.

.. note::

   Make sure you do not sanitize custom variables that intentionally create directories,
   (i.e. sanitizing ``/path/to/tv_shows/``) otherwise they will... be sanitized and not
   resolve to directories!


Using Scripting Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Let's suppose you are an avid command-line user, and like all of your file names to be
``snake_cased_with_no_spaces``. We can use the `replace
<https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#replace>`_
*scripting function* to create and use a snake-cased title.

.. code-block:: yaml

   output_options:
     output_directory: "/path/to/tv_shows/{subscription_name_sanitized}"
     file_name: "{custom_file_name}.{ext}"
     thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

   overrides:
     snake_cased_title: >-
       {
         %replace( title, ' ', '_' )
       }
     custom_file_name: "{upload_date_standardized}_{snake_cased_title_sanitized}"

Scripting functions are similar to variables - they must be used within curly-braces.
It is good practice to use ``>-`` when defining variables that use functions. It is
YAML's way of saying:

- Allow a string to be multi-lined, and do not include newlines before or after it.

See for yourself `here
<https://yaml-online-parser.appspot.com/?yaml=output_options%3A%0A%20%20output_directory%3A%20%22%7Bsubscription_name_sanitized%7D%22%0A%20%20file_name%3A%20%22%7Bcustom_file_name%7D.%7Bext%7D%22%0A%20%20thumbnail_name%3A%20%22%7Bcustom_file_name%7D.%7Bthumbnail_ext%7D%22%0A%0Aoverrides%3A%0A%20%20snake_cased_title%3A%20%3E-%0A%20%20%20%20%7B%0A%20%20%20%20%20%20%25replace%28%20title%2C%20%27%20%27%2C%20%27_%27%20%29%0A%20%20%20%20%7D%0A%20%20custom_file_name%3A%20%22%7Bupload_date_standardized%7D%20%7Bsnake_cased_title_sanitized%7D%22&type=json>`_.
Any whitespace within curly-braces is okay since it will be parsed out. This is needed
to make scripting function usage readable.

.. important::

   It is important to use ``>-`` over other YAML new-line directives like ``>`` because
   they add newlines before or after curly-braces, and will be included in your
   variable's output string.


Advanced Scripting
------------------

Accessing ``info.json`` Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The entirety of an entry's ``info.json`` file resides in the `Map
<https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_types.html#map>`_
variable `entry_metadata
<https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/entry_variables.html#entry-metadata>`_.

Any field can be accessed by using the `map_get
<https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#map-get>`_
function like so:

.. code-block:: yaml
  :caption:
     Fetches the 'artist' value from the .info.json, returns null if it does not exist.

   artist: >-
     { %map_get( entry_metadata, "artist", null ) }

Creating Custom Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Custom functions can be created in the overrides section using the following syntax:

.. code-block:: yaml

   overrides:
     "%get_entry_metadata_field": >-
       { %map_get( entry_metadata, $0, null ) }

Custom function definitions must have ``%`` as a prefix to the function name, be
surrounded by quotes to make YAML parsing happy, and can support arguments using ``$0``,
``$1``, ... to indicate their first argument, second argument, etc.

Using our new custom function, we can simply the ``artist`` variable definition above to:

.. code-block:: yaml

   overrides:
     "%get_entry_metadata_field": >-
       { %map_get( entry_metadata, $0, null ) }
     artist: >-
       { get_entry_metadata_field("artist") }
