
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

  .. tab-item:: Same-Line

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

   For non-String types, they must be defined as parameters to scripting functions. This is because
   anything in a variable definition that is not within curly-braces gets evaluated as a String.

Integer
~~~~~~~

Integers are whole numbers with no decimal.

.. tab-set::

  .. tab-item:: Multi-Line

    .. code-block:: yaml

       int_variable: >-
         {
           %int(2022)
         }

  .. tab-item:: New-Line

    .. code-block:: yaml

       int_variable: >-
         { %int(2022) }


  .. tab-item:: Same-Line

    .. code-block:: yaml

       int_variable: "{ %int(2022) }"

Float
~~~~~

Floats are floating-point decimals numbers.

.. tab-set::

  .. tab-item:: Multi-Line

    .. code-block:: yaml

       float_variable: >-
         {
           %float(3.14)
         }

  .. tab-item:: New-Line

    .. code-block:: yaml

       float_variable: >-
         { %float(3.14) }

  .. tab-item:: Same-Line

    .. code-block:: yaml

       float_variable: "{ %float(3.14) }"

Boolean
~~~~~~~

A type is considered boolean if it spells out ``True`` or ``False``, case-insensitive.

.. tab-set::

  .. tab-item:: Multi-Line

    .. code-block:: yaml

       bool_variable: >-
         {
           %bool(True)
         }

  .. tab-item:: New-Line

    .. code-block:: yaml

       bool_variable: >-
         { %bool(True) }

  .. tab-item:: Same-Line

    .. code-block:: yaml

       bool_variable: "{ %bool(FALSE) }"

Array
~~~~~

An Array contains multiple types of any kind, including nested Arrays and Maps.
Arrays are defined using brackets (``[ ]``), and are accessed using zero-based indexing.

.. tab-set::

  .. tab-item:: Multi-Line

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

  .. tab-item:: New-Line

    .. code-block:: yaml

       array_variable: >-
         { ["element with index 0", 1, 2.0, ["Nested Array 3"]] }
       element_0: >-
         { %array_at(array_variable, 0) }

  .. tab-item:: Same-Line

    .. code-block:: yaml

       array_variable: "{ ['element with index 0', 1, 2.0, ['Nested Array 3' ]] }"
       element_0: "{ %array_at(array_variable, 0) }"

Map
~~~

A Map is a key-value store, containing mappings between keys and values.
Maps are defined using curley-braces (``{ }``), and are accessed using their keys.

.. tab-set::

  .. tab-item:: Multi-Line

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

  .. tab-item:: New-Line

    .. code-block:: yaml

       map_variable: >-
         { {"string_key": "string_value", 1: "int_key", "list_value": ["elem0", 1, 2.0]} }
       string_value: >-
         { %map_get(map_variable, "string_key") }

  .. tab-item:: Same-Line

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

  .. tab-item:: New-Line

    .. code-block:: yaml

      null_variable: >-
        { %string(null) }

  .. tab-item:: Same-Line

    .. code-block:: yaml

      null_variable: "{ %string(null) }"


Function Type-Hints
-------------------

AnyArgument
~~~~~~~~~~~
AnyArgument means any of the above Types are valid as input or output to a scripting function.

.. note::

   Strict typing is enforced. For functions that return ``AnyArgument`` need to be casted before
   passing into functions that expect a particular type.

Numeric
~~~~~~~
Numeric refers to either an Integer or Float.

Optional
~~~~~~~~
Optional means a particular scripting function argument can be either provided or not included.
For example, the function
`map_get <https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#map-get>`_
has an optional default value. Both of these usages are valid:

.. tab-set::

  .. tab-item:: Map Get

    .. code-block:: yaml

       will_throw_key_does_not_exist_error: "{ %map_get( {}, 'key' ) }"

  .. tab-item:: Map Get with Optional Default Value

    .. code-block:: yaml

      will_return_default: "{ %map_get( {}, 'key', 'default value' ) }"

Lambda
~~~~~~
Lambda parameters are a reference to a function, and will call that lambda function
on the input. In this example,

.. code-block:: yaml

   lambda_array_numeric_to_string: >-
     {
       %array_apply( [ 1, 2, 3, 4], %string )
     }

We apply ``%string`` as a lambda function to
`array_apply <https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#array-apply>`_,
which is called on every element in the input array. The output becomes ``["1", "2", "3", "4"]``.

This example has one input-argument being passed into the lambda. For other lambda-based functions
like `array_enumerate <https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#array-enumerate>`_,
it expects the lambda function to have two input arguments. These are denoted using
``LambdaTwo``, ``LambdaThree``, etc within the function spec.

LambdaReduce
~~~~~~~~~~~~
LambdaReduce is special type of lambda that reduces an Array to a single value by calling the
LabmdaReduce function repeatedly on two elements in the Array until it is reduced to a single value.

In this example,

.. code-block:: yaml

   lambda_reduce_sum: >-
     {
       %array_reduce( [ 1, 2, 3, 4], %add )
     }

We call
`array_reduce <https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#array-reduce>`_
on the input array, using
`add <https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#add>`_
as the LambdaReduce function. This will reduce the Array to a single value by internally calling

.. code-block::

   - %add(1, 2) = 3
   - %add(3, 3) = 6
   - %add(6, 4) = 10

And evaluate to ``10``.

ReturnableArguments
~~~~~~~~~~~~~~~~~~~

Returnable arguments are used in conditional functions like
`if <https://ytdl-sub.readthedocs.io/en/latest/config_reference/scripting/scripting_functions.html#if>`_,
which implies the argument passed into the function is the function's output. For example,

.. code-block:: yaml

   conditional_function: >-
     {
       %if( True, "Return this if True", "Return this if False" )
     }

is going to return ``"Return this if True"`` since the condition parameter is ``True``.