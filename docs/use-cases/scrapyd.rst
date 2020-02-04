Download data to a remote server
================================

You can use a Scrapyd instance to run your scrapers.

Configure Scrapyd
-----------------

Make sure you have Scrapyd running somewhere. It needs to run in an environment that also has the ``requests`` package.

If you want to post to Kingfisher Process, you will also need some environmental variables - see the output section.

Configure Local Scripts
-----------------------

Setup the details to access scrapyd in scrapy.cfg. By default, in this repository, this is:

.. code-block:: ini

    [deploy]
    url = http://localhost:6800/
    project = kingfisher

Deploying Spiders
-----------------

The code must be packaged up and deployed to the server:

.. code-block:: bash

    scrapyd-deploy 

Scheduling a run
----------------

Replacing ``spider_name`` with a spider's name like ``canada_buyandsell`` and ``NAME`` with your name:

.. code-block:: bash

    $ curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d note="Started by NAME."
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

To run a sample run, add ``-d sample-true``, for example:

.. code-block:: bash

    $ curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d note="Started by NAME." -d sample=true
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

Update the note with your name, and anything else of interest.

Find out more in the `Scrapyd docs <https://scrapyd.readthedocs.io/en/latest/overview.html#scheduling-a-spider-run>`_.

Output - Disk
-------------

You must configure FILES_STORE.

.. code-block:: python

    FILES_STORE = '/scrapyd/data'

FILES_STORE should be a local folder that data will appear in. It should be a full path, and the scrapyd process should have permissions to write there.

Files are stored in ``{FILES_STORE}/{scraper_name}/{scraper_start_date_time}``.

Output - Kingfisher Process
---------------------------

In settings.py, make sure the 3 API variables are set to load from the environment. For example:

.. code-block:: python

    KINGFISHER_API_URI = os.environ.get('KINGFISHER_API_URI')
    KINGFISHER_API_KEY = os.environ.get('KINGFISHER_API_KEY')
    KINGFISHER_API_LOCAL_DIRECTORY = os.environ.get('KINGFISHER_API_LOCAL_DIRECTORY')


The ``kingfisher-process`` API endpoint variables are currently accessed from the scrapyd environment. To configure:

1. Copy ``env.sh.tmpl`` to ``env.sh``
2. Set the ``KINGFISHER_*`` variables in ``env.sh`` to match your instance (local or server).
3. Run ``source env.sh`` to export them to the scrapyd environment.
