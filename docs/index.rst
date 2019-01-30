OCDS Kingfisher Scrapers
========================

This repo contains scrapers for OCDS data from various publishers, using the `Scrapy <https://scrapy.org/>`_ crawler framework. 

Initially sources are based on those in `OCDS Kingfisher <https://github.com/open-contracting/kingfisher>`_.

The scrapers can save the downloaded files to disk for you to use your own analysis tools on.

The scrapers can also post their results to an instance of `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_,
where things like checks, transforms, and storage in a database can take place.
See `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_ for specifics, as well as how to install your own ``kingfisher-process`` instance.


.. toctree::

   setup.rst
   use-standalone.rst
   use-scrapyd.rst
   use-hosted.rst
   use-scrapycloud.rst
   writing-scrapers.rst
