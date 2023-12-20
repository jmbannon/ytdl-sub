Environment Agnostic
====================

PIP Install
--------------
You can install our
`PyPI package <https://pypi.org/project/ytdl-sub/>`_.
Both ffmpeg and Python 3.10 or greater are required.

.. code-block:: bash

  python3 -m pip install -U ytdl-sub

Local Install
--------------
With a Python 3.10 virtual environment, you can clone and install the repo.

.. code-block:: bash

  git clone https://github.com/jmbannon/ytdl-sub.git
  cd ytdl-sub

  pip install -e .

Local Docker Build
-------------------
Run ``make docker`` in the root directory of this repo to build the image. This
will build the python wheel and install it in the Dockerfile.

.. code-block:: bash

  git clone https://github.com/jmbannon/ytdl-sub.git
  cd ytdl-sub

  make docker