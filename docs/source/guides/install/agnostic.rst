====================
Environment Agnostic
====================

The PIP install method is not recommended; use of this method may cause unintended
requirement conflicts if you have other locally installed apps that depend on ffmpeg.


PIP Install
--------------

You can install our `PyPI package <https://pypi.org/project/ytdl-sub/>`_.  Both ffmpeg
and Python 3.10 or greater are required.

.. code-block:: bash

  python3 -m pip install -U ytdl-sub

Install for Development
=======================

These environment-agnostic methods of installing ``ytdl-sub`` are meant for local
development of ``ytdl-sub``. If you want to contribute your changes, please read
:doc:`/guides/development/index`.

Local Install
--------------

With a Python 3.10 virtual environment, you can clone and install the repo.

.. code-block:: bash

  git clone https://github.com/jmbannon/ytdl-sub.git
  cd ytdl-sub

  pip install -e .

Local Docker Build
-------------------

Run ``make docker`` in the root directory of this repo to build the image. This will
build the python wheel and install it in the Dockerfile.

.. code-block:: bash

  git clone https://github.com/jmbannon/ytdl-sub.git
  cd ytdl-sub

  make docker
