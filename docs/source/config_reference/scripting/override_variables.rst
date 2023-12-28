
Override Variables
==================

subscription_indent_i
---------------------
For subscriptions in the form of

.. code-block:: yaml

   Preset | = Indent Value 1:
     = Indent Value 2:
       "Subscription Name": "https://..."

``subscription_indent_1`` and ``subscription_indent_2`` get set to
``Indent Value 1`` and ``Indent Value 2``.

subscription_name
-----------------
Name of the subscription

subscription_value
------------------
For subscriptions in the form of

.. code-block:: yaml

   "Subscription Name": "https://..."

``subscription_value`` gets set to ``https://...``.

subscription_value_i
--------------------
For subscriptions in the form of

.. code-block:: yaml

   "Subscription Name":
     - "https://url1.com/..."
     - "https://url2.com/..."

``subscription_value_1`` and ``subscription_value_2`` get set to ``https://url1.com/...``
and ``https://url2.com/...``. Note that ``subscription_value_1`` also gets set to
``subscription_value``.
