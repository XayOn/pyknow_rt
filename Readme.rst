pyknow_rt
-----------------------------

.. image:: https://travis-ci.org/XayOn/pyknow_rt.svg?branch=master
    :target: https://travis-ci.org/XayOn/pyknow_rt

.. image:: https://coveralls.io/repos/github/XayOn/pyknow_rt/badge.svg?branch=master
 :target: https://coveralls.io/github/XayOn/pyknow_rt?branch=master

.. image:: https://badge.fury.io/py/pyknow_rt.svg
    :target: https://badge.fury.io/py/pyknow_rt

Real time pyknow with rethinkdb


Usage
-----

::

    pyknow_rt.

    Real time pyknow with rethinkdb

    Usage: pyknow_rt [options]


Distributing
------------

Distribution may be done in the usual setuptools way.
If you don't want to use pipenv, just use requirements.txt file as usual and
remove Pipfile, setup.py will auto-detect Pipfile removal and won't try to
update requirements.

Note that, to enforce compatibility between PBR and Pipenv, this updates the
tools/pip-requires and tools/test-requires files each time you do a *dist*
command

General notes
--------------

This package uses PBR and pipenv.
Pipenv can be easily replaced by a virtualenv by keeping requirements.txt
instead of using pipenv flow.
If you don't need, or you're not actually using git + setuptools distribution
system, you can enable PBR manual versioning by creating a METADATA file with
content like::

    Name: pyknow_rt
    Version: 0.0.1

Generating documentation
------------------------

This package contains a extra-requires section specifiying doc dependencies.
There's a special hook in place that will automatically install them whenever
we try to build its dependencies, thus enabling us to simply execute::

        pipenv run python setup.py build_sphinx

to install documentation dependencies and buildd HTML documentation in docs/build/


Passing tests
--------------

Running tests should always be done inside pipenv.
This package uses behave for TDD and pytest for unit tests, you can execute non-wip
tests and behavioral tests using::

        pipenv run python setup.py test


Docker
------

This package can be run with docker.

Default entry_point will be executed (pyknow_rt) by default

This builds the docker for a SPECIFIC distributable release, that you need to
have previously built.

For this, do a release::

    python setup.py sdist

Grab the redistributable files::

    distrib=($(/bin/ls -t dist))

Now run docker build with it::

    docker build --build-arg distfile=${distrib[1]}
