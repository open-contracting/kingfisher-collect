kingfisher-scrape for OCDS
==========================

kingfisher-scrape is a tool to download OCDS data from various sources, and to store it on disk and/or send it to an instance of `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_. 

It is built using the `Scrapy <https://scrapy.org/>`_ crawler framework.

It can be used standalone, for development or testing of scrapers. For production use, we recommend using scrapyd. It is possible to use kingfisher-scrape on the hosted scrapycloud service, however the restrictions of this service mean that it's not suitable for all scrapers. 

OCP operate a hosted instance of kingfisher-scrape, which is available to OCP staff and the OCDS Team. For information about how to access this, see the `hosted kingfisher documentation <https://ocdskingfisher.readthedocs.io/en/latest/#hosted-kingfisher>`_


.. toctree::

   setup.rst
   use-standalone.rst
   use-scrapyd.rst
   use-hosted.rst
   use-scrapycloud.rst
   writing-scrapers.rst
