..
  WARNING: This RST file is generated from docstrings in:
    src/ytdl_sub/entries/variables/override_variables.py
  In order to make a change to this file, edit the respective docstring
  and run `make docs`. This will automatically sync the Python RST-based
  docstrings into this file.

Static Variables
================

Subscription Variables
----------------------

subscription_array
~~~~~~~~~~~~~~~~~~
For subscriptions in the form of

.. code-block:: yaml

   "Subscription Name":
     - "https://url1.com/..."
     - "https://url2.com/..."

Store all values into an array named ``subscription_array``.

subscription_has_download_archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Returns True if the subscription has any entries recorded in a download archive. False
otherwise.

subscription_indent_i
~~~~~~~~~~~~~~~~~~~~~
For subscriptions in the form of

.. code-block:: yaml

   Preset | = Indent Value 1:
     = Indent Value 2:
       "Subscription Name": "https://..."

``subscription_indent_1`` and ``subscription_indent_2`` get set to
``Indent Value 1`` and ``Indent Value 2``.

subscription_map
~~~~~~~~~~~~~~~~
For subscriptions in the form of

.. code-block:: yaml

   + Subscription Name:
     Music Videos:
       - "https://url1.com/..."
     Concerts:
       - "https://url2.com/..."

Stores all the contents under the subscription name into the override variable
``subscription_map`` as a Map value. The above example is stored as:

.. code-block:: python

   {
     "Music Videos": [
       "https://url1.com/..."
     ],
     "Concerts: [
       "https://url2.com/..."
     ]
   }

subscription_name
~~~~~~~~~~~~~~~~~
Name of the subscription. For subscriptions types that use a prefix (``~``, ``+``),
the prefix and all whitespace afterwards is stripped from the subscription name.

subscription_value
~~~~~~~~~~~~~~~~~~
For subscriptions in the form of

.. code-block:: yaml

   "Subscription Name": "https://..."

``subscription_value`` gets set to ``https://...``.

subscription_value_i
~~~~~~~~~~~~~~~~~~~~
For subscriptions in the form of

.. code-block:: yaml

   "Subscription Name":
     - "https://url1.com/..."
     - "https://url2.com/..."

``subscription_value_1`` and ``subscription_value_2`` get set to ``https://url1.com/...``
and ``https://url2.com/...``. Note that ``subscription_value_1`` also gets set to
``subscription_value``.
