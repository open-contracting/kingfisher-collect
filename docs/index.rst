kingfisher-scrape for OCDS
==========================

kingfisher-scrape is a tool to download OCDS data from various sources, and to store it on disk and/or send it to an instance of `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_. 

It is built using the `Scrapy <https://scrapy.org/>`_ crawler framework.

It can be used standalone, for development or testing of scrapers. For production use, we recommend using scrapyd.

OCP operate a hosted instance of kingfisher-scrape, which is available to OCP staff and the OCDS Team. For information about how to access this, see the `hosted kingfisher documentation <https://ocdskingfisher.readthedocs.io/en/latest/#hosted-kingfisher>`_

The developers have tested kingfisher-scrape on `Scrapy Cloud <https://scrapinghub.com/scrapy-cloud>`_ and it works, but the limitations of the service (specifically, not being able to write to a readable file storage and send to the Process API at the same time) mean that it's not suitable for OCP use. Community users may, however, find this a helpful service.

.. toctree::

   setup.rst
   sources.rst
   use-standalone.rst
   use-scrapyd.rst
   use-hosted.rst
   use-scrapycloud.rst
   writing-scrapers.rst
   old.rst
