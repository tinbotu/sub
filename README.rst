=================
NotSubKulture bot
=================

.. image:: https://api.travis-ci.org/tinbotu/sub.svg
   :target: https://travis-ci.org/tinbotu/sub

DevServer Setup
---------------

Requirements

- Vagrant > 1.6

::

    main-machine: ~/work$ git clone ${THIS_REPOSITORY}
    main-machine: ~/work/sub$ vagrant up
    main-machine: ~/work/sub$ vagrant ssh
    subculture: ~$ cd /vagrant
    subculture:/vagrant$ make test


for Lingr
---------

Server Requirements
-------------------

Ubuntu 14.04

Packages are listed on scripts/devserver_provisioning.sh
