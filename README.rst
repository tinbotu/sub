=================
NotSubculture bot
=================

.. image:: https://github.com/tinbotu/sub/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/tinbotu/sub/actions/workflows/ci.yml

A chat bot for Lingr / Slack. Incoming messages are matched against a
dictionary of patterns in ``sun.py`` and dispatched to the response
classes under ``subculture/``.

Requirements
------------

- Python 3.10+
- Redis
- MeCab (``libmecab-dev`` / ``mecab-ipadic-utf8``)

Setup
-----

::

    git clone ${THIS_REPOSITORY}
    cd sub
    make setup        # creates ./bin venv and installs requirements
    cp settings.yaml.skel settings.yaml
    cp bot_secret.yaml.skel bot_secret.yaml
    make test

Docker
------

::

    docker build -t sub .
    docker run --rm sub        # boots redis and runs the test suite

The bot itself is served as a CGI script (``sun.cgi`` -> ``sun.py``).
