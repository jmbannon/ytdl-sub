Development and Contributing
============================


Requirements
------------

- python >= 3.10
- ffmpeg/ffprobe 4.4.5 (test checksums rely on this version)
- make


Local Install
-------------
.. tab-set-code::

    .. code-block:: shell

        pip install -e .[test,lint,docs]

    .. code-block:: zsh

        pip install -e .\[test,lint,docs\]


Linter
------

All source code contributed must be formatted to our linter specification.  Run the
following to auto-format and check for any issues with your code:

.. code-block:: shell

   make lint


Adding Documentation
--------------------

Docs can be found in ``ytdl-sub/docs/source/``, and are built using the command:


.. code-block:: shell
   :caption:
      Viewable at http://localhost:63342/ytdl-sub/docs/build/html/index.html once built

   make docs

Some of the documentation is built using doc-strings from the python source code. The
above command will rebuild those as well.


Testing
-------
Tests are written using pytest. Many of them evaluate checksums of output files to ensure no unintended
changes are introduced to the way ``ytdl-sub`` produces files. This checksum can be inaccurate for
end-to-end tests, but are reliable for integration tests.

If integration tests are failing, ensure...

- you're using the correct ffmpeg version
- you are developing on Linux or Mac (have not tested windows yet)
- your local ``ytdl-sub`` dependencies are up-to-date


IDE Setup
---------

PyCharm is our preferred IDE. The codebase is simple enough to where it's not required,
but is highly recommended.

TODO: screenshots of configuration


Debugging
---------

Debug Logs
^^^^^^^^^^

Run with ``--log-level debug`` to show all debug logs when running ytdl-sub.


Reproducing a Failing Subscription
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subscriptions will dump their entire *compiled* yaml at the beginning of exeuction when
using ``--log-level debug``. This can be copy-pasted into the file
``resources/file_fixtures/repro.yaml``.

Running the test ``e2e.test_debug_repro.TestReproduce.test_debug_log_repro`` will fully
reproduce that subscription in order to debug it.
