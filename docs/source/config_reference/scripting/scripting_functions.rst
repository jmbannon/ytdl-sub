
Scripting Functions
===================

Array Functions
---------------

array
~~~~~
:spec: ``array(maybe_array: AnyArgument) -> Array``

:description:
  Tries to cast an unknown variable type to an Array.

array_apply
~~~~~~~~~~~
:spec: ``array_apply(array: Array, lambda_function: Lambda) -> Array``

:description:
  Apply a lambda function on every element in the Array.
:usage:

.. code-block:: python

   {
     %array_apply( [1, 2, 3] , %string )
   }

   # ["1", "2", "3"]

array_apply_fixed
~~~~~~~~~~~~~~~~~
:spec: ``array_apply_fixed(array: Array, fixed_argument: AnyArgument, lambda2_function: LambdaTwo, reverse_args: Optional[Boolean]) -> Array``

:description:
  Apply a lambda function on every element in the Array, with ``fixed_argument``
  passed as a second argument to every invocation.

array_at
~~~~~~~~
:spec: ``array_at(array: Array, idx: Integer, default: Optional[AnyArgument]) -> AnyArgument``

:description:
  Return the element in the Array at index ``idx``. If ``idx`` exceeds the array length,
  either return ``default`` if provided or throw an error.

array_contains
~~~~~~~~~~~~~~
:spec: ``array_contains(array: Array, value: AnyArgument) -> Boolean``

:description:
  Return True if the value exists in the Array. False otherwise.

array_enumerate
~~~~~~~~~~~~~~~
:spec: ``array_enumerate(array: Array, lambda_function: LambdaTwo) -> Array``

:description:
  Apply a lambda function on every element in the Array, where each arg
  passed to the lambda function is ``idx, element`` as two separate args.

array_extend
~~~~~~~~~~~~
:spec: ``array_extend(arrays: Array, ...) -> Array``

:description:
  Combine multiple Arrays into a single Array.

array_first
~~~~~~~~~~~
:spec: ``array_first(array: Array, fallback: AnyArgument) -> AnyArgument``

:description:
  Returns the first element whose boolean conversion is True. Returns fallback
  if all elements evaluate to False.

array_flatten
~~~~~~~~~~~~~
:spec: ``array_flatten(array: Array) -> Array``

:description:
  Flatten any nested Arrays into a single-dimensional Array.

array_index
~~~~~~~~~~~
:spec: ``array_index(array: Array, value: AnyArgument) -> Integer``

:description:
  Return the index of the value within the Array if it exists. If it does not, it will
  throw an error.

array_overlay
~~~~~~~~~~~~~
:spec: ``array_overlay(array: Array, overlap: Array, only_missing: Optional[Boolean]) -> Array``

:description:
  Overlaps ``overlap`` onto ``array``. Can optionally only overlay missing indices.

array_product
~~~~~~~~~~~~~
:spec: ``array_product(arrays: Array, ...) -> Array``

:description:
  Returns the Cartesian product of elements from different arrays

array_reduce
~~~~~~~~~~~~
:spec: ``array_reduce(array: Array, lambda_reduce_function: LambdaReduce) -> AnyArgument``

:description:
  Apply a reduce function on pairs of elements in the Array, until one element remains.
  Executes using the left-most and reduces in the right direction.

array_reverse
~~~~~~~~~~~~~
:spec: ``array_reverse(array: Array) -> Array``

:description:
  Reverse an Array.

array_size
~~~~~~~~~~
:spec: ``array_size(array: Array) -> Integer``

:description:
  Returns the size of an Array.

array_slice
~~~~~~~~~~~
:spec: ``array_slice(array: Array, start: Integer, end: Optional[Integer]) -> Array``

:description:
  Returns the slice of the Array.

----------------------------------------------------------------------------------------------------

Boolean Functions
-----------------

and
~~~
:spec: ``and(values: AnyArgument, ...) -> Boolean``

:description:
  ``and`` operator. Returns True if all values evaluate to True. False otherwise.

bool
~~~~
:spec: ``bool(value: AnyArgument) -> Boolean``

:description:
  Cast any type to a Boolean.

eq
~~
:spec: ``eq(left: AnyArgument, right: AnyArgument) -> Boolean``

:description:
  ``==`` operator. Returns True if left == right. False otherwise.

gt
~~
:spec: ``gt(left: AnyArgument, right: AnyArgument) -> Boolean``

:description:
  ``>`` operator. Returns True if left > right. False otherwise.

gte
~~~
:spec: ``gte(left: AnyArgument, right: AnyArgument) -> Boolean``

:description:
  ``>=`` operator. Returns True if left >= right. False otherwise.

is_array
~~~~~~~~
:spec: ``is_array(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is a Map. False otherwise.

is_bool
~~~~~~~
:spec: ``is_bool(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is a Float. False otherwise.

is_float
~~~~~~~~
:spec: ``is_float(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is a Float. False otherwise.

is_int
~~~~~~
:spec: ``is_int(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is an Integer. False otherwise.

is_map
~~~~~~
:spec: ``is_map(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is a Map. False otherwise.

is_null
~~~~~~~
:spec: ``is_null(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is null (i.e. an empty string). False otherwise.

is_numeric
~~~~~~~~~~
:spec: ``is_numeric(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is either an Integer or Float. False otherwise.

is_string
~~~~~~~~~
:spec: ``is_string(value: AnyArgument) -> Boolean``

:description:
  Returns True if a value is a String. False otherwise.

lt
~~
:spec: ``lt(left: AnyArgument, right: AnyArgument) -> Boolean``

:description:
  ``<`` operator. Returns True if left < right. False otherwise.

lte
~~~
:spec: ``lte(left: AnyArgument, right: AnyArgument) -> Boolean``

:description:
  ``<=`` operator. Returns True if left <= right. False otherwise.

ne
~~
:spec: ``ne(left: AnyArgument, right: AnyArgument) -> Boolean``

:description:
  ``!=`` operator. Returns True if left != right. False otherwise.

not
~~~
:spec: ``not(value: Boolean) -> Boolean``

:description:
  ``not`` operator. Returns the opposite of value.

or
~~
:spec: ``or(values: AnyArgument, ...) -> Boolean``

:description:
  ``or`` operator. Returns True if any value evaluates to True. False otherwise.

xor
~~~
:spec: ``xor(values: AnyArgument, ...) -> Boolean``

:description:
  ``^`` operator. Returns True if exactly one value is set to True. False otherwise.

----------------------------------------------------------------------------------------------------

Conditional Functions
---------------------

elif
~~~~
:spec: ``elif(if_elif_else: AnyArgument, ...) -> AnyArgument``

:description:
  Conditional ``if`` statement that is capable of doing else-ifs (``elif``) via
  adjacent arguments. It is expected for there to be an odd number of arguments >= 3 to
  supply at least one conditional and an else.
:usage:

  .. code-block:: python

     %elif(
        condition1,
        return1,
        condition2,
        return2,
        ...
        else_return
     )

if
~~
:spec: ``if(condition: Boolean, true: ReturnableArgumentA, false: ReturnableArgumentB) -> Union[ReturnableArgumentA, ReturnableArgumentB]``

:description:
  Conditional ``if`` statement that returns the ``true`` or ``false`` parameter
  depending on the ``condition`` value.

if_passthrough
~~~~~~~~~~~~~~
:spec: ``if_passthrough(maybe_true_arg: ReturnableArgumentA, else_arg: ReturnableArgumentB) -> Union[ReturnableArgumentA, ReturnableArgumentB]``

:description:
  Conditional ``if`` statement that returns the ``maybe_true_arg`` if it evaluates to True,
  otherwise returns ``else_arg``.

----------------------------------------------------------------------------------------------------

Date Functions
--------------

datetime_strftime
~~~~~~~~~~~~~~~~~
:spec: ``datetime_strftime(posix_timestamp: Integer, date_format: String) -> String``

:description:
  Converts a posix timestamp to a date using strftime formatting.

----------------------------------------------------------------------------------------------------

Error Functions
---------------

assert
~~~~~~
:spec: ``assert(value: ReturnableArgument, assert_message: String) -> ReturnableArgument``

:description:
  Explicitly throw an error with the provided assert message if ``value`` evaluates to
  False. If it evaluates to True, it will return ``value``.

assert_eq
~~~~~~~~~
:spec: ``assert_eq(value: ReturnableArgument, equals: AnyArgument, assert_message: String) -> ReturnableArgument``

:description:
  Explicitly throw an error with the provided assert message if ``value`` does not equal
  ``equals``. If they do equal, then return ``value``.

assert_ne
~~~~~~~~~
:spec: ``assert_ne(value: ReturnableArgument, equals: AnyArgument, assert_message: String) -> ReturnableArgument``

:description:
  Explicitly throw an error with the provided assert message if ``value`` equals
  ``equals``. If they do equal, then return ``value``.

assert_then
~~~~~~~~~~~
:spec: ``assert_then(value: AnyArgument, ret: ReturnableArgument, assert_message: String) -> ReturnableArgument``

:description:
  Explicitly throw an error with the provided assert message if ``value`` evaluates to
  False. If it evaluates to True, it will return ``ret``.

throw
~~~~~
:spec: ``throw(error_message: String) -> AnyArgument``

:description:
  Explicitly throw an error with the provided error message.

----------------------------------------------------------------------------------------------------

Json Functions
--------------

from_json
~~~~~~~~~
:spec: ``from_json(argument: String) -> AnyArgument``

:description:
  Converts a JSON string into an actual type.

----------------------------------------------------------------------------------------------------

Map Functions
-------------

map
~~~
:spec: ``map(maybe_mapping: AnyArgument) -> Map``

:description:
  Tries to cast an unknown variable type to a Map.

map_apply
~~~~~~~~~
:spec: ``map_apply(mapping: Map, lambda_function: LambdaTwo) -> Array``

:description:
  Apply a lambda function on the Map, where each arg
  passed to the lambda function is ``key, value`` as two separate args.

map_contains
~~~~~~~~~~~~
:spec: ``map_contains(mapping: Map, key: AnyArgument) -> Boolean``

:description:
  Returns True if the key is in the Map. False otherwise.

map_enumerate
~~~~~~~~~~~~~
:spec: ``map_enumerate(mapping: Map, lambda_function: LambdaThree) -> Array``

:description:
  Apply a lambda function on the Map, where each arg
  passed to the lambda function is ``idx, key, value`` as three separate args.

map_extend
~~~~~~~~~~
:spec: ``map_extend(maps: Map, ...) -> Map``

:description:
  Return maps combined in the order from left-to-right. Duplicate keys will use the
  right-most map's value.

map_get
~~~~~~~
:spec: ``map_get(mapping: Map, key: AnyArgument, default: Optional[AnyArgument]) -> AnyArgument``

:description:
  Return ``key``'s value within the Map. If ``key`` does not exist, and ``default`` is
  provided, it will return ``default``. Otherwise, will error.

map_get_non_empty
~~~~~~~~~~~~~~~~~
:spec: ``map_get_non_empty(mapping: Map, key: AnyArgument, default: AnyArgument) -> AnyArgument``

:description:
  Return ``key``'s value within the Map. If ``key`` does not exist or is an empty string,
  return ``default``. Otherwise, will error.

map_size
~~~~~~~~
:spec: ``map_size(mapping: Map) -> Integer``

:description:
  Returns the size of a Map.

----------------------------------------------------------------------------------------------------

Numeric Functions
-----------------

add
~~~
:spec: ``add(values: Numeric, ...) -> Numeric``

:description:
  ``+`` operator. Returns the sum of all values.

div
~~~
:spec: ``div(left: Numeric, right: Numeric) -> Numeric``

:description:
  ``/`` operator. Returns ``left / right``.

float
~~~~~
:spec: ``float(value: AnyArgument) -> Float``

:description:
  Cast to Float.

int
~~~
:spec: ``int(value: AnyArgument) -> Integer``

:description:
  Cast to Integer.

max
~~~
:spec: ``max(values: Numeric, ...) -> Numeric``

:description:
  Returns max of all values.

min
~~~
:spec: ``min(values: Numeric, ...) -> Numeric``

:description:
  Returns min of all values.

mod
~~~
:spec: ``mod(left: Numeric, right: Numeric) -> Numeric``

:description:
  ``%`` operator. Returns ``left % right``.

mul
~~~
:spec: ``mul(values: Numeric, ...) -> Numeric``

:description:
  ``*`` operator. Returns the product of all values.

pow
~~~
:spec: ``pow(base: Numeric, exponent: Numeric) -> Numeric``

:description:
  ``**`` operator. Returns the exponential of the base and exponent value.

sub
~~~
:spec: ``sub(values: Numeric, ...) -> Numeric``

:description:
  ``-`` operator. Subtracts all values from left to right.

----------------------------------------------------------------------------------------------------

Regex Functions
---------------

regex_capture_groups
~~~~~~~~~~~~~~~~~~~~
:spec: ``regex_capture_groups(regex: String) -> Integer``

:description:
  Returns number of capture groups in regex

regex_capture_many
~~~~~~~~~~~~~~~~~~
:spec: ``regex_capture_many(string: String, regex_array: Array, default: Optional[Array]) -> Array``

:description:
  Returns the input string and first regex's capture groups that match to the string
  in an array. If a default is not provided, then all number of regex capture groups
  must be equal across all regex strings. In addition, an error will be thrown if
  no matches are found.

  If the default is provided, then the number of capture groups must be less than
  or equal to the length of the default value array. Any element not captured
  will return the respective default value.
:usage:

.. code-block:: python

   {
     %regex_capture_many(
       "2020-02-27",
       [
         "No (.*) matches here",
         "([0-9]+)-([0-9]+)-27"
       ],
       [ "01", "01" ]
     )
   }

   # ["2020-02-27", "2020", "02"]

regex_capture_many_required
~~~~~~~~~~~~~~~~~~~~~~~~~~~
:spec: ``regex_capture_many_required(string: String, regex_array: Array) -> Array``

:description:
  Deprecated. Use %regex_capture_many instead.

regex_capture_many_with_defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:spec: ``regex_capture_many_with_defaults(string: String, regex_array: Array, default: Optional[Array]) -> Array``

:description:
  Deprecated. Use %regex_capture_many instead.

regex_fullmatch
~~~~~~~~~~~~~~~
:spec: ``regex_fullmatch(regex: String, string: String) -> Array``

:description:
  Checks for entire string to be a match. If a match exists, returns
  the string as the first element of the Array. If there are capture groups, returns each
  group as a subsequent element in the Array.

regex_match
~~~~~~~~~~~
:spec: ``regex_match(regex: String, string: String) -> Array``

:description:
  Checks for a match only at the beginning of the string. If a match exists, returns
  the string as the first element of the Array. If there are capture groups, returns each
  group as a subsequent element in the Array.

regex_search
~~~~~~~~~~~~
:spec: ``regex_search(regex: String, string: String) -> Array``

:description:
  Checks for a match anywhere in the string. If a match exists, returns
  the string as the first element of the Array. If there are capture groups, returns each
  group as a subsequent element in the Array.

regex_search_any
~~~~~~~~~~~~~~~~
:spec: ``regex_search_any(string: String, regex_array: Array) -> Boolean``

:description:
  Returns True if any regex pattern in the regex array matches the string. False otherwise.

regex_sub
~~~~~~~~~
:spec: ``regex_sub(regex: String, replacement: String, string: String) -> String``

:description:
  Returns the string obtained by replacing the leftmost non-overlapping occurrences of the
  pattern in string by the replacement string. The replacement string can reference the
  match groups via backslash escapes. Callables as replacement argument are not supported.

----------------------------------------------------------------------------------------------------

String Functions
----------------

capitalize
~~~~~~~~~~
:spec: ``capitalize(string: String) -> String``

:description:
  Capitalize the first character in the string.

concat
~~~~~~
:spec: ``concat(values: String, ...) -> String``

:description:
  Concatenate multiple Strings into a single String.

contains
~~~~~~~~
:spec: ``contains(string: String, contains: String) -> Boolean``

:description:
  Returns True if ``contains`` is in ``string``. False otherwise.

contains_any
~~~~~~~~~~~~
:spec: ``contains_any(string: String, contains_array: Array) -> Boolean``

:description:
    Returns true if any element in ``contains_array`` is in ``string``. False otherwise.

lower
~~~~~
:spec: ``lower(string: String) -> String``

:description:
  Lower-case the entire String.

pad
~~~
:spec: ``pad(string: String, length: Integer, char: String) -> String``

:description:
  Pads the string to the given length

pad_zero
~~~~~~~~
:spec: ``pad_zero(numeric: Numeric, length: Integer) -> String``

:description:
  Pads a numeric with zeros to the given length

replace
~~~~~~~
:spec: ``replace(string: String, old: String, new: String, count: Optional[Integer]) -> String``

:description:
  Replace the ``old`` part of the String with the ``new``. Optionally only replace it
  ``count`` number of times.

slice
~~~~~
:spec: ``slice(string: String, start: Integer, end: Optional[Integer]) -> String``

:description:
  Returns the slice of the Array.

split
~~~~~
:spec: ``split(string: String, sep: String, max_split: Optional[Integer]) -> Array``

:description:
  Splits the input string into multiple strings.

string
~~~~~~
:spec: ``string(value: AnyArgument) -> String``

:description:
  Cast to String.

titlecase
~~~~~~~~~
:spec: ``titlecase(string: String) -> String``

:description:
  Capitalize each word in the string.

upper
~~~~~
:spec: ``upper(string: String) -> String``

:description:
  Upper-case the entire String.

----------------------------------------------------------------------------------------------------

Ytdl-Sub Functions
------------------

legacy_bracket_safety
~~~~~~~~~~~~~~~~~~~~~
:spec: ``legacy_bracket_safety(value: ReturnableArgument) -> ReturnableArgument``

ytdl-sub used to replace brackets ('{', '}') with unicode brackets ('｛', '｝') to not
interfere with its legacy variable scripting system. This function replicates that
behavior.

sanitize
~~~~~~~~
:spec: ``sanitize(value: AnyArgument) -> String``

Sanitize a string using yt-dlp's ``sanitize_filename`` method to ensure it's safe to use
for file/directory names on any OS.

sanitize_plex_episode
~~~~~~~~~~~~~~~~~~~~~
:spec: ``sanitize_plex_episode(string: String) -> String``

Sanitize a string using ``sanitize`` and replace numerics with their respective fixed-width
numbers. This is used to have Plex avoid scraping numbers like ``4x4`` as the
season and/or episode.

to_date_metadata
~~~~~~~~~~~~~~~~
:spec: ``to_date_metadata(yyyymmdd: String) -> Map``

Takes a date in the form of YYYYMMDD and returns a Map containing:

- date (String, YYYYMMDD)
- date_standardized (String, YYYY-MM-DD)
- year (Integer)
- month (Integer)
- day (Integer)
- year_truncated (Integer, YY from YY[YY])
- month_padded (String)
- day_padded (String)
- year_truncated_reversed (Integer, 100 - year_truncated)
- month_reversed (Integer, 13 - month)
- month_reversed_padded (String)
- day_reversed (Integer, total_days_in_month + 1 - day)
- day_reversed_padded (String)
- day_of_year (Integer)
- day_of_year_padded (String, padded 3)
- day_of_year_reversed (Integer, total_days_in_year + 1 - day_of_year)
- day_of_year_reversed_padded (String, padded 3)

to_native_filepath
~~~~~~~~~~~~~~~~~~
:spec: ``to_native_filepath(filepath: String) -> String``

Convert any unix-based path separators ('/') with the OS's native
separator. In addition, expand ~ to absolute directories.

truncate_filepath_if_too_long
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:spec: ``truncate_filepath_if_too_long(filepath: String) -> String``

If a file-path is too long for the OS, this function will truncate it while preserving
the extension.
