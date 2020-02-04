Use - Standalone
================

You can use Scrapy in standalone mode, where you run the process directly.

Doing this does not let you take full advantage of scrapy but it can be useful for testing or places where it is hard to install or use other software.

Running
-------

Scrapy provides a commandline interface for spiders.

To see available spiders:

.. code-block:: bash

    scrapy list

To run one:

.. code-block:: bash

    scrapy crawl spider_name -a key=value

For example, replacing ``spider_name`` with a spider's name like ``canada_buyandsell`` and ``NAME`` with your name:

.. code-block:: bash

    scrapy crawl spider_name -a note="Started by NAME." -a sample=true
    scrapy crawl spider_name -a note="Started by NAME."

Update the note with your name, and anything else of interest.

Output - Disk
-------------

You must configure FILES_STORE.

.. code-block:: python

    FILES_STORE = 'data'

FILES_STORE should be a local folder that data will appear in.

Files are stored in ``{FILES_STORE}/{scraper_name}/{scraper_start_date_time}``.


Output - Kingfisher Process
---------------------------

In settings.py, make sure the 3 API variables are set to load from the environment. For example:

.. code-block:: python

    KINGFISHER_API_URI = os.environ.get('KINGFISHER_API_URI')
    KINGFISHER_API_KEY = os.environ.get('KINGFISHER_API_KEY')
    KINGFISHER_API_LOCAL_DIRECTORY = os.environ.get('KINGFISHER_API_LOCAL_DIRECTORY')


The ``kingfisher-process`` API endpoint variables are currently accessed from the scraper's environment. To configure:

1. Copy ``env.sh.tmpl`` to ``env.sh``
2. Set the ``KINGFISHER_*`` variables in ``env.sh`` to match your instance (local or server).
3. Run ``source env.sh`` to export them to the scraper environment.
