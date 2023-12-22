
Scripting Functions
===================

Array Functions
---------------

array
~~~~~
``array(maybe_array: AnyArgument) -> Array``

Tries to cast an unknown variable type to an Array.

array_apply
~~~~~~~~~~~
``array_apply(array: Array, lambda_function: Lambda) -> Array``

Apply a lambda function on every element in the Array.

array_at
~~~~~~~~
``array_at(array: Array, idx: Integer) -> AnyArgument``

Return the element in the Array at index ``idx``.

array_contains
~~~~~~~~~~~~~~
``array_contains(array: Array, value: AnyArgument) -> Boolean``

Return True if the value exists in the Array. False otherwise.

array_enumerate
~~~~~~~~~~~~~~~
``array_enumerate(array: Array, lambda_function: LambdaTwo) -> Array``

Apply a lambda function on every element in the Array, where each arg
passed to the lambda function is ``idx, element`` as two separate args.

array_extend
~~~~~~~~~~~~
``array_extend(arrays: Array, ...) -> Array``

Combine multiple Arrays into a single Array.

array_flatten
~~~~~~~~~~~~~
``array_flatten(array: Array) -> Array``

Flatten any nested Arrays into a single-dimensional Array.

array_index
~~~~~~~~~~~
``array_index(array: Array, value: AnyArgument) -> Integer``

Return the index of the value within the Array if it exists. If it does not, it will
throw an error.

array_product
~~~~~~~~~~~~~
``array_product(arrays: Array, ...) -> Array``

Returns the Cartesian product of elements from different arrays

array_reduce
~~~~~~~~~~~~
``array_reduce(array: Array, lambda_reduce_function: LambdaReduce) -> AnyArgument``

Apply a reduce function on pairs of elements in the Array, until one element remains.
Executes using the left-most and reduces in the right direction.

array_reverse
~~~~~~~~~~~~~
``array_reverse(array: Array) -> Array``

Reverse an Array.

array_size
~~~~~~~~~~
``array_size(array: Array) -> Integer``

Returns the size of an Array.

array_slice
~~~~~~~~~~~
``array_slice(array: Array, start: Integer, end: Optional[Integer]) -> Array``

Returns the slice of the Array.

Boolean Functions
-----------------

and
~~~
``and(values: AnyArgument, ...) -> Boolean``

``and`` operator. Returns True if all values evaluate to True. False otherwise.

bool
~~~~
``bool(value: AnyArgument) -> Boolean``

Cast any type to a Boolean.

eq
~~
``eq(left: AnyArgument, right: AnyArgument) -> Boolean``

``==`` operator. Returns True if left == right. False otherwise.

gt
~~
``gt(left: AnyArgument, right: AnyArgument) -> Boolean``

``>`` operator. Returns True if left > right. False otherwise.

gte
~~~
``gte(left: AnyArgument, right: AnyArgument) -> Boolean``

``>=`` operator. Returns True if left >= right. False otherwise.

lt
~~
``lt(left: AnyArgument, right: AnyArgument) -> Boolean``

``<`` operator. Returns True if left < right. False otherwise.

lte
~~~
``lte(left: AnyArgument, right: AnyArgument) -> Boolean``

``<=`` operator. Returns True if left <= right. False otherwise.

ne
~~
``ne(left: AnyArgument, right: AnyArgument) -> Boolean``

``!=`` operator. Returns True if left != right. False otherwise.

not
~~~
``not(value: Boolean) -> Boolean``

``not`` operator. Returns the opposite of value.

or
~~
``or(values: AnyArgument, ...) -> Boolean``

``or`` operator. Returns True if any value evaluates to True. False otherwise.

xor
~~~
``xor(values: AnyArgument, ...) -> Boolean``

``^`` operator. Returns True if exactly one value is set to True. False otherwise.

Conditional Functions
---------------------

if
~~
``if(condition: Boolean, true: ReturnableArgumentA, false: ReturnableArgumentB) -> Union[ReturnableArgumentA, ReturnableArgumentB]``

Conditional ``if`` statement that returns the ``true`` or ``false`` parameter
depending on the ``condition`` value.

if_passthrough
~~~~~~~~~~~~~~
``if_passthrough(maybe_true_arg: ReturnableArgumentA, else_arg: ReturnableArgumentB) -> Union[ReturnableArgumentA, ReturnableArgumentB]``

Conditional ``if`` statement that returns the ``maybe_true_arg`` if it evaluates to True,
otherwise returns ``else_arg``.

Date Functions
--------------

datetime_strftime
~~~~~~~~~~~~~~~~~
``datetime_strftime(posix_timestamp: Integer, date_format: String) -> String``

Converts a posix timestamp to a date using strftime formatting.

Error Functions
---------------

assert
~~~~~~
``assert(value: ReturnableArgument, assert_message: String) -> ReturnableArgument``

Explicitly throw an error with the provided assert message if ``value`` evaluates to False.
If it evaluates to True, it will return ``value``.

throw
~~~~~
``throw(error_message: String) -> AnyArgument``

Explicitly throw an error with the provided error message.

Json Functions
--------------

from_json
~~~~~~~~~
``from_json(argument: String) -> AnyArgument``

Converts a JSON string into an actual type.

Map Functions
-------------

map
~~~
``map(maybe_mapping: AnyArgument) -> Map``

Tries to cast an unknown variable type to a Map.

map_apply
~~~~~~~~~
``map_apply(mapping: Map, lambda_function: LambdaTwo) -> Array``

Apply a lambda function on the Map, where each arg
passed to the lambda function is ``key, value`` as two separate args.

map_contains
~~~~~~~~~~~~
``map_contains(mapping: Map, key: AnyArgument) -> Boolean``

Returns True if the key is in the Map. False otherwise.

map_enumerate
~~~~~~~~~~~~~
``map_enumerate(mapping: Map, lambda_function: LambdaThree) -> Array``

Apply a lambda function on the Map, where each arg
passed to the lambda function is ``idx, key, value`` as three separate args.

map_get
~~~~~~~
``map_get(mapping: Map, key: AnyArgument, default: Optional[AnyArgument]) -> AnyArgument``

Return ``key``'s value within the Map. If ``key`` does not exist, and ``default`` is
provided, it will return ``default``. Otherwise, will error.

map_get_non_empty
~~~~~~~~~~~~~~~~~
``map_get_non_empty(mapping: Map, key: AnyArgument, default: AnyArgument) -> AnyArgument``

Return ``key``'s value within the Map. If ``key`` does not exist or is an empty string,
return ``default``. Otherwise, will error.

map_size
~~~~~~~~
``map_size(mapping: Map) -> Integer``

Returns the size of a Map.

Numeric Functions
-----------------

add
~~~
``add(values: Numeric, ...) -> Numeric``

``+`` operator. Returns the sum of all values.

div
~~~
``div(left: Numeric, right: Numeric) -> Numeric``

``/`` operator. Returns ``left / right``.

float
~~~~~
``float(value: AnyArgument) -> Float``

Cast to Float.

int
~~~
``int(value: AnyArgument) -> Integer``

Cast to Integer.

max
~~~
``max(values: Numeric, ...) -> Numeric``

Returns max of all values.

min
~~~
``min(values: Numeric, ...) -> Numeric``

Returns min of all values.

mod
~~~
``mod(left: Numeric, right: Numeric) -> Numeric``

``%`` operator. Returns ``left % right``.

mul
~~~
``mul(values: Numeric, ...) -> Numeric``

``*`` operator. Returns the product of all values.

pow
~~~
``pow(base: Numeric, exponent: Numeric) -> Numeric``

``**`` operator. Returns the exponential of the base and exponent value.

sub
~~~
``sub(values: Numeric, ...) -> Numeric``

``-`` operator. Subtracts all values from left to right.

Regex Functions
---------------

regex_fullmatch
~~~~~~~~~~~~~~~
``regex_fullmatch(regex: String, string: String) -> Array``

Checks for entire string to be a match. If a match exists, returns
the string as the first element of the Array. If there are capture groups, returns each
group as a subsequent element in the Array.

regex_match
~~~~~~~~~~~
``regex_match(regex: String, string: String) -> Array``

Checks for a match only at the beginning of the string. If a match exists, returns
the string as the first element of the Array. If there are capture groups, returns each
group as a subsequent element in the Array.

regex_search
~~~~~~~~~~~~
``regex_search(regex: String, string: String) -> Array``

Checks for a match anywhere in the string. If a match exists, returns
the string as the first element of the Array. If there are capture groups, returns each
group as a subsequent element in the Array.

String Functions
----------------

capitalize
~~~~~~~~~~
``capitalize(string: String) -> String``

Capitalize the first character in the string.

concat
~~~~~~
``concat(values: String, ...) -> String``

Concatenate multiple Strings into a single String.

lower
~~~~~
``lower(string: String) -> String``

Lower-case the entire String.

pad
~~~
``pad(string: String, length: Integer, char: String) -> String``

Pads the string to the given length

pad_zero
~~~~~~~~
``pad_zero(numeric: Numeric, length: Integer) -> String``

Pads a numeric with zeros to the given length

replace
~~~~~~~
``replace(string: String, old: String, new: String, count: Optional[Integer]) -> String``

Replace the ``old`` part of the String with the ``new``. Optionally only replace it
``count`` number of times.

slice
~~~~~
``slice(string: String, start: Integer, end: Optional[Integer]) -> String``

Returns the slice of the Array.

string
~~~~~~
``string(value: AnyArgument) -> String``

Cast to String.

titlecase
~~~~~~~~~
``titlecase(string: String) -> String``

Capitalize each word in the string.

upper
~~~~~
``upper(string: String) -> String``

Upper-case the entire String.

Ytdl-Sub Functions
------------------

legacy_bracket_safety
~~~~~~~~~~~~~~~~~~~~~
``legacy_bracket_safety(value: ReturnableArgument) -> ReturnableArgument``

ytdl-sub used to replace brackets ('{', '}') with unicode brackets ('｛', '｝') to not
interfere with its legacy variable scripting system. This function replicates that
behavior.

sanitize
~~~~~~~~
``sanitize(value: AnyArgument) -> String``

Sanitize a string using yt-dlp's ``sanitize_filename`` method to ensure it's safe to use
for file/directory names on any OS.

sanitize_plex_episode
~~~~~~~~~~~~~~~~~~~~~
``sanitize_plex_episode(string: String) -> String``

Sanitize a string using ``sanitize`` and replace numerics with their respective fixed-width
numbers. This is used to have Plex avoid scraping numbers like ``4x4`` as the
season and/or episode.

to_date_metadata
~~~~~~~~~~~~~~~~
``to_date_metadata(yyyymmdd: String) -> Map``

Takes a date in the form of YYYYMMDD and returns a Map containing:

- date (String, YYYYMMDD)
- date_standardized (String, YYYY-MM-DD)
- year (Integer)
- month (Integer)
- day (Integer)
- year_truncated (String, YY from YY[YY])
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
``to_native_filepath(filepath: String) -> String``

Convert any unix-based path separators ('/') with the OS's native
separator.

truncate_filepath_if_too_long
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``truncate_filepath_if_too_long(filepath: String) -> String``

If a file-path is too long for the OS, this function will truncate it while preserving
the extension.
