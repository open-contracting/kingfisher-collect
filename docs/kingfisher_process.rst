.. _kingfisher-process:

Integrate with Kingfisher Process
=================================

Besides storing the scraped data on disk, you can also send them to an instance of `Kingfisher Process <https://kingfisher-process.readthedocs.io/>`_ for processing.

Version 1
---------

You need to deploy an instance of Kingfisher Process, including its `web app <https://kingfisher-process.readthedocs.io/en/latest/web.html#web-app>`__. Then, set the following either as environment variables or as Scrapy settings in ``kingfisher_scrapy.settings.py``:

``KINGFISHER_API_URI``
  The URL from which Kingfisher Process' `web app <https://kingfisher-process.readthedocs.io/en/latest/web.html#web-app>`_ is served. Do not include a trailing slash.
``KINGFISHER_API_KEY``
  One of the API keys in Kingfisher Process' `API_KEYS <https://kingfisher-process.readthedocs.io/en/latest/config.html#web-api>`__ setting.

To run a spider:

.. code-block:: bash

   env KINGFISHER_API_URI='http://127.0.0.1:5000' KINGFISHER_API_KEY=1234 scrapy crawl spider_name

To add a note to the collection in Kingfisher Process:

.. code-block:: bash

   scrapy crawl spider_name -a note='Started by NAME.'
