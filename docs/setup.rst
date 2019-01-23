.. _setup:

Install
=======

.. code-block:: bash

   pip install -r requirements.txt 

Configure
=========

File storage
------------

If you want to change where downloaded JSON is stored on disc, edit the ``FILES_STORE`` variable in ``settings.py``.

Kingfisher process
------------------

The scrapers post their results to an instance of `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_, where things like validation, normalisation, and storage in a database can take place. See `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_ for specifics, as well as how to install your own ``kingfisher-process`` instance (and note that this is a work in progress).

The ``kingfisher-process`` API endpoint variables are currently accessed from the scraper's environment. To configure:

1. Rename ``env.sh.tmpl`` to ``env.sh``
2. Set the ``KINGFISHER_*`` variables in ``env.sh`` to match your instance (local or server).
3. Run ``source env.sh`` to export them to the scraper environment.

This is *optional*. If you don't set the ``KINGFISHER_*`` variables, this part of the pipeline is automatically disabled, and scraper results will still be saved to disc.