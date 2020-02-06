Download data to your computer
==============================

This page will guide you through installing Kingfisher Scrape and using it to collect data from data sources.

How it works
------------

Kingfisher Scrape is built on the `Scrapy <https://scrapy.org/>`_ framework. Using this framework, we have authored "spiders" that you can run in order to "crawl" data sources and extract OCDS data.

When collecting data from a data source, each of its OCDS files will be written to a separate file on your computer. (Depending on the data source, an OCDS file might be a `record package <https://standard.open-contracting.org/latest/en/schema/record_package/>`__, `release package <https://standard.open-contracting.org/latest/en/schema/release_package/>`__, individual `record <https://standard.open-contracting.org/latest/en/schema/records_reference/>`__ or individual `release <https://standard.open-contracting.org/latest/en/schema/reference/>`__.)

By default, these files are written to a ``data`` directory (you can :ref:`change this<configure>`) within your ``kingfisher-scrape`` directory (which you create :ref:`during installation<install>`). Each spider creates its own directory within the ``data`` directory, and each crawl of a given spider creates its own directory within its spider's directory. For example, if you run the ``zambia`` spider (:ref:`see below<collect-data>`), then the directory hierarchy will look like:

.. code-block:: none

   kingfisher-scrape/
   └── data
       └── zambia
           └── 20200102_030405
               ├── <...>.json
               ├── <...>.fileinfo
               └── <...>

As you can see, the ``data`` directory contains a ``zambia`` spider directory (matching the spider's name), which in turn contains a ``20200102_030405`` crawl directory (matching the time at which you started the crawl – in this case, 2020-01-02 03:04:05).

The crawl's directory has ``.json`` and ``.fileinfo`` files. The JSON files are the OCDS data. Each ``.fileinfo`` file contains metadata about a corresponding JSON file: the URL at which the JSON file was retrieved, along with other details.

.. _install:

Install
-------

To use Kingfisher Scrape, you need access to a `Unix-like shell <https://en.wikipedia.org/wiki/Shell_(computing)>`__ (some are available for Windows). `Git <https://git-scm.com>`__ and `Python <https://www.python.org>`__ (version 3.6 or greater) must be installed.

When ready, open a shell, and run:

.. code-block:: bash

   git clone https://github.com/open-contracting/kingfisher-scrape.git
   cd kingfisher-scrape
   pip install -r requirements.txt

The next steps assume that you have changed to the ``kingfisher-scrape`` directory (the ``cd`` command above).

.. _configure:

Configure
---------

To use a different directory than the ``data`` directory to store files, change the ``FILES_STORE`` variable in the ``kingfisher_scrapy/settings.py`` file. It can be a relative path (like ``data``) or an absolute path (like ``/home/user/path``).

.. code-block:: python

   FILES_STORE = '/home/user/path'

.. _collect-data:

Collect data
------------

You're now ready to collect data!

To list the spiders, run:

.. code-block:: bash

    scrapy list

Alternately, you can get the list of spiders by accessing the ``kingfisher_scrapy/spiders`` directory in the `GitHub repository <https://github.com/open-contracting/kingfisher-scrape/tree/master/kingfisher_scrapy/spiders>`_. Each ``.py`` file is a spider, and the part before the ``.py`` extension is the spider's name.

The spiders' names might be ambiguous. If you're unsure which spider to run, you can compare their names to the list of `OCDS publishers <https://www.open-contracting.org/worldwide/#/table>`__, or contact the OCDS Helpdesk at data@open-contracting.org.

To run a spider (that is, start a "crawl"), replace ``spider_name`` below with the name of a spider from ``scrapy list`` above:

.. code-block:: bash

    scrapy crawl spider_name

To download only a sample of the available data, add the ``sample=true`` spider argument:

.. code-block:: bash

    scrapy crawl spider_name -a sample=true

Scrapy will then output a log of its activity.

Using data
----------

You should now have a crawl directory within the ``data`` directory containing OCDS files. For help using data, read about `using open contracting data <https://www.open-contracting.org/data/data-use/>`__.
