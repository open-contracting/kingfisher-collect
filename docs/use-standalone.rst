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

    scrapy crawl <spider_name> -a key=value

eg.

.. code-block:: bash

    scrapy crawl canada_buyandsell -a sample=true
    scrapy crawl canada_buyandsell

Output - Disk
-------------

In settings.py, make sure ``ITEM_PIPELINES`` includes ``KingfisherFilesPipeline`` and that ``FILES_STORE`` is set. For example:

.. code-block:: python

    ITEM_PIPELINES = {
        'kingfisher_scrapy.pipelines.KingfisherFilesPipeline': 2,
    }

    FILES_STORE = 'data'

FILES_STORE should be a local folder that data will appear in.

Files are stored in ``{FILES_STORE}/{scraper_name}/{scraper_start_date_time}``.


Output - Kingfisher Process
---------------------------

In order to use this, you must also set up the Disk output.

In settings.py, make sure ``ITEM_PIPELINES`` includes ``KingfisherPostPipeline`` and that the 2 API variables are set to load from the environment. For example:

.. code-block:: python

    ITEM_PIPELINES = {
        'kingfisher_scrapy.pipelines.KingfisherFilesPipeline': 2,
        'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 3,
    }

    KINGFISHER_API_URI = os.environ.get('KINGFISHER_API_URI')
    KINGFISHER_API_KEY = os.environ.get('KINGFISHER_API_KEY')


The ``kingfisher-process`` API endpoint variables are currently accessed from the scraper's environment. To configure:

1. Copy ``env.sh.tmpl`` to ``env.sh``
2. Set the ``KINGFISHER_*`` variables in ``env.sh`` to match your instance (local or server).
3. Run ``source env.sh`` to export them to the scraper environment.
