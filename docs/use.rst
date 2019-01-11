Use
===

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


Output
======

Scraped JSON is stored on disc, as it was found. Files are stored in ``{project_root}/data/{scraper_name}/{scraper_start_date_time}``. The ``/data/`` part can be configured in ``settings.py`` with ``FILES_STORE``.

Scrapers also post the downloaded JSON files, and a bunch of metadata, to a `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_ endpoint (see setup_ for how to configure this).