=========
Scripting
=========

``ytdl-sub`` fields (file-names, tags, etc) are defined using variables and scripts. The links below
contain reference documentation for each built-in variable and scripting function.

.. toctree::
  :maxdepth: 1

  entry_variables
  override_variables
  scripting_functions

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
     output_directory: "Custom YTDL-SUB TV Show"

Static Variables
~~~~~~~~~~~~~~~~

``ytdl-sub`` offers a few built-in static variables, including ``subscription_name``.
We can use this instead of hard-coding it above:

.. code-block:: yaml

   output_options:
     output_directory: "{subscription_name}"

The syntax for variable usage is brackets with the variable name within it. Assuming
our subscription is actually named "Custom YTDL-SUB TV Show", then ``ytdl-sub``
will actually write to that directory.

Entry Variables
~~~~~~~~~~~~~~~

For context, an *entry* is a video or audio file downloaded from ``yt-dlp``.
*Entry variables* are variables that are derived from an entry's ``info.json`` file. This file
comes from ``yt-dlp`` and contains every piece of metadata that it scraped.

These variables are not considered static since they change per entry download. There are a
few fields in ``ytdl-sub`` (i.e. ``output_directory``) that must be static. For others,
we are free to use values that derive from an entry.

Suppose we want to customize the name of an entry's output file and thumbnail to include its
title in its name. We can do that using entry variables:

.. code-block:: yaml

   output_options:
     output_directory: "{subscription_name}"
     file_name: "{title}.{ext}"
     thumbnail_name: "{title}.{thumbnail_ext}"

Sanitizing Variables
~~~~~~~~~~~~~~~~~~~~

For experienced ``yt-dlp`` scrapers, you may be thinking:

- "what if the title has characters that do not play nice with my operating system?"

``ytdl-sub`` is able to *sanitize* any variable, meaning it strips any bad characters out
and can be used for file names. We can ensure our file names and directories by using:

.. code-block:: yaml

   output_options:
     output_directory: "{subscription_name_sanitized}"
     file_name: "{title_sanitized}.{ext}"
     thumbnail_name: "{title_sanitized}.{thumbnail_ext}"

Simply add a ``_sanitized`` suffix to any variable name to make it sanitized.

Creating Custom Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we want to include the date in our file names. This means we'd need to update
both the ``file_name`` and ``thumbnail_name`` fields to include it.

Instead, we can create a custom *override variable*. This is ``ytdl-sub``'s method
for creating and overriding custom variables.

These are created in the ``overrides`` section. Let's take our above example and create
a ``custom_file_name`` variable to use for the entry file and thumbnail fields:

.. code-block:: yaml

   output_options:
     output_directory: "{subscription_name_sanitized}"
     file_name: "{custom_file_name}.{ext}"
     thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

   overrides:
     custom_file_name: "{upload_date_standardized} {title_sanitized}"

Using Scripting Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Let's suppose you are an avid command-line user, and like all of your file names to be
``snake_cased_with_no_spaces``. We can use *scripting functions* to create and use a snake-cased
title.

.. code-block:: yaml

   output_options:
     output_directory: "{subscription_name_sanitized}"
     file_name: "{custom_file_name}.{ext}"
     thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

   overrides:
     snake_cased_title: >-
       {
         %replace( title, ' ', '_' )
       }
     custom_file_name: "{upload_date_standardized} {snake_cased_title_sanitized}"

You will notice that we use `>-`. This is YAML's way to say "allow a string to be multi-lined