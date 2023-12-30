
Scripting Types
===============

Types
-----

String
~~~~~~

Strings are a series of characters surrounded by quotes and can be defined in a few ways, including:

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

      string_variable: "This is a String variable"

  .. tab-item:: In-Line

    .. code-block:: yaml

      string_variable: "{ %string('This is a String variable') }"

  .. tab-item:: Single Quote

    .. code-block:: yaml

      string_variable: >-
        {
          %string('This is a String variable')
        }

  .. tab-item:: Double Quote

    .. code-block:: yaml

      string_variable: >-
        {
          %string("This is a String variable")
        }

  .. tab-item:: Triple Quote

    .. code-block:: yaml

      string_variable: >-
        {
          %string('''This is a String variable''')
        }

  .. tab-item:: Triple-Double Quote

    .. code-block:: yaml

      string_variable: >-
        {
          %string("""This is a String variable""")
        }

.. note::

   For non-String types, they must be defined using scripting functions. This is because
   anything in a variable definition that is not within curly-braces gets evaluated as a String.

Integer
~~~~~~~

Integers are whole numbers with no decimal.

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

       int_variable: >-
         {
           %int(2022)
         }

  .. tab-item:: In-Line

    .. code-block:: yaml

       int_variable: "{ %int(2022) }"

Float
~~~~~

Floats are floating-point decimals numbers.

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

       float_variable: >-
         {
           %float(3.14)
         }

  .. tab-item:: In-Line

    .. code-block:: yaml

       float_variable: "{ %float(3.14) }"

Boolean
~~~~~~~

A type is considered boolean if it spells out ``True`` or ``False``, case-insensitive.

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

       bool_variable: >-
         {
           %bool(True)
         }

  .. tab-item:: In-Line

    .. code-block:: yaml

       bool_variable: "{ %bool(FALSE) }"

Array
~~~~~

An Array contains multiple types of any kind, including nested Arrays and Maps.
Arrays are defined using brackets (``[ ]``), and are accessed using zero-based indexing.

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

       array_variable: >-
         {
           [
             "element with index 0",
             1,
             2.0,
             [ "Nested Array 3" ]
           ]
         }
       element_0: >-
         {
           %array_at(array_variable, 0)
         }

  .. tab-item:: In-Line

    .. code-block:: yaml

       array_variable: "{ ['element with index 0', 1, 2.0, ['Nested Array 3' ]] }"
       element_0: "{ %array_at(array_variable, 0) }"

Map
~~~

A Map is a key-value store, containing mappings between keys and values.
Maps are defined using curley-braces (``{ }``), and are accessed using their keys.

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

       map_variable: >-
         {
           {
             "string_key": "string_value",
             1: "int_key",
             "list_value": [ "elem0", 1, 2.0 ]
           }
         }
       string_value: >-
         {
           %map_get(map_variable, "string_key")
         }

  .. tab-item:: In-Line

    .. code-block:: yaml

       map_variable: "{ {'string_key': 'string_value', 1: 'int_key', 'list_value': [ 'elem0', 1, 2.0 ]} }"
       string_value: "{ %map_get(map_variable, 'string_key') }"

Null
~~~~
Null is represented by an empty String, and can be conveyed by spelling out ``null``,
case-insensitive.

.. tab-set::

  .. tab-item:: Literal

    .. code-block:: yaml

       null_variable: ""

  .. tab-item:: In-Line

    .. code-block:: yaml

      null_variable: "{ %string(null) }"


Union Types
-----------

AnyArgument
~~~~~~~~~~~
AnyArgument means any of the above Types are valid as input or output to a scripting function.

Numeric
~~~~~~~
Numeric refers to either an Integer or Float.

Optional
~~~~~~~~
Optional means a particular scripting function argument can be either provided or not included.

Lambdas
-------

Lambda
~~~~~~
WIP

LambdaTwo
~~~~~~~~~

LambdaThree
~~~~~~~~~~~

LambdaReduce
~~~~~~~~~~~~

ReturnableArguments
-------------------

Returnable arguments are used in conditional functions like ``%if``, which implies the argument
passed into the function is the function's output.


