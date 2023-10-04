OCDS Kingfisher Collect
=======================

.. include:: ../README.rst

You can:

-  :doc:`Download data to your computer, by installing Kingfisher Collect<local>`
-  :doc:`Download data to a remote server, by using Scrapyd<scrapyd>`
-  :doc:`Integrate with Kingfisher Process<kingfisher_process>`

Instead of installing Kingfisher Collect to your computer, you can `follow this interactive step-by-step guide <https://colab.research.google.com/drive/1bN5C9h5YLUF9YpIprAeOMZcXJ5Tr6iaO>`__, to use Kingfisher Collect in `Google Colaboratory <https://research.google.com/colaboratory/faq.html>`__.

You can also try using Kingfisher Collect with `Scrapy Cloud <https://scrapinghub.com/scrapy-cloud>`_.

.. _how-it-works:

How it works
------------

Kingfisher Collect is built on the `Scrapy <https://scrapy.org/>`_ framework. Using this framework, we have authored "spiders" that you can run in order to "crawl" data sources and extract OCDS data.

When collecting data from a data source, each of its OCDS files will be written to a separate file on your computer. Kingfisher Collect also ensures that the files are always either a `record package <https://standard.open-contracting.org/latest/en/schema/record_package/>`__ or a `release package <https://standard.open-contracting.org/latest/en/schema/release_package/>`__, depending on the source.

By default, these files are written to a ``data`` directory (you can :ref:`change this<configure>`) within your ``kingfisher-collect`` directory (which you will create :ref:`during installation<install>`). Each spider creates its own directory within the ``data`` directory, and each crawl of a given spider creates its own directory within its spider's directory. For example, if you run the ``zambia`` spider (:ref:`learn how<collect-data>`), then the directory hierarchy will look like:

.. code-block:: none

   kingfisher-collect/
   └── data
       └── zambia
           └── 20200102_030405
               └── C8E
               └── D1D
                   └── <...>.json
                   └── <...>

As you can see, the ``data`` directory contains a ``zambia`` spider directory (matching the spider's name), which in turn contains a ``20200102_030405`` crawl directory (matching the time at which you started the crawl – in this case, 2020-01-02 03:04:05), then a subdirectory is created by creating a 3-characters long hash for each scraped file name. The crawl directory contains ``.json`` files – the OCDS data.

.. toctree::
   :caption: Contents
   :maxdepth: 2

   local.rst
   scrapyd.rst
   spiders.rst
   logs.rst
   cli.rst
   kingfisher_process.rst
   contributing/index.rst
   history.rst
