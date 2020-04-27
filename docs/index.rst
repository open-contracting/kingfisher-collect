OCDS Kingfisher Collect
=======================

.. include:: ../README.rst

You can:

-  :doc:`Download data to your computer, by installing Kingfisher Collect<local>`
-  :doc:`Download data to a remote server, by using Scrapyd<scrapyd>`

You can also try using Kingfisher Collect with `Scrapy Cloud <https://scrapinghub.com/scrapy-cloud>`_.

How it works
------------

Kingfisher Collect is built on the `Scrapy <https://scrapy.org/>`_ framework. Using this framework, we have authored "spiders" that you can run in order to "crawl" data sources and extract OCDS data.

When collecting data from a data source, each of its OCDS files will be written to a separate file on your computer. (Depending on the data source, an OCDS file might be a `record package <https://standard.open-contracting.org/latest/en/schema/record_package/>`__, `release package <https://standard.open-contracting.org/latest/en/schema/release_package/>`__, individual `record <https://standard.open-contracting.org/latest/en/schema/records_reference/>`__ or individual `release <https://standard.open-contracting.org/latest/en/schema/reference/>`__.)

By default, these files are written to a ``data`` directory (you can :ref:`change this<configure>`) within your ``kingfisher-collect`` directory (which you will create :ref:`during installation<install>`). Each spider creates its own directory within the ``data`` directory, and each crawl of a given spider creates its own directory within its spider's directory. For example, if you run the ``zambia`` spider (:ref:`learn how<collect-data>`), then the directory hierarchy will look like:

.. code-block:: none

   kingfisher-collect/
   └── data
       └── zambia
           └── 20200102_030405
               ├── <...>.json
               ├── <...>.fileinfo
               └── <...>

As you can see, the ``data`` directory contains a ``zambia`` spider directory (matching the spider's name), which in turn contains a ``20200102_030405`` crawl directory (matching the time at which you started the crawl – in this case, 2020-01-02 03:04:05).

The crawl's directory will contain ``.json`` and ``.fileinfo`` files. The JSON files are the OCDS data. Each ``.fileinfo`` file contains metadata about a corresponding JSON file: the URL at which the JSON file was retrieved, along with other details.

.. toctree::
   :caption: Contents
   :maxdepth: 2

   local.rst
   scrapyd.rst
   spiders.rst
   crawl-report-guide.rst
   writing-scrapers.rst
   api/index.rst
