Download data to your computer
==============================

This page will guide you through installing Kingfisher Scrape and using it to collect data from data sources.

.. _install:

Install Kingfisher Scrape
-------------------------

To use Kingfisher Scrape, you need access to a `Unix-like shell <https://en.wikipedia.org/wiki/Shell_(computing)>`__ (some are available for Windows). `Git <https://git-scm.com>`__ and `Python <https://www.python.org>`__ (version 3.6 or greater) must be installed.

When ready, open a shell, and run:

.. code-block:: bash

   git clone https://github.com/open-contracting/kingfisher-scrape.git
   cd kingfisher-scrape
   pip install -r requirements.txt

The next steps assume that you have changed to the ``kingfisher-scrape`` directory (the ``cd`` command above).

.. _configure:

Configure Kingfisher Scrape
---------------------------

.. note::

   This step is optional.

To use a different directory than the default ``data`` directory to store files, change the ``FILES_STORE`` variable in the ``kingfisher_scrapy/settings.py`` file. It can be a relative path (like ``data``) or an absolute path (like ``/home/user/path``).

.. code-block:: python

   FILES_STORE = '/home/user/path'

.. _collect-data:

Collect data
------------

You're now ready to collect data!

To list the spiders, run:

.. code-block:: bash

    scrapy list

The spiders' names might be ambiguous. If you're unsure which spider to run, you can compare their names to the list of `OCDS publishers <https://www.open-contracting.org/worldwide/#/table>`__, or `contact the OCDS Helpdesk <data@open-contracting.org>`__.

To run a spider (that is, to start a "crawl"), replace ``spider_name`` below with the name of a spider from ``scrapy list`` above:

.. code-block:: bash

    scrapy crawl spider_name

.. _sample:

Download a sample
~~~~~~~~~~~~~~~~~

To download only a sample of the available data, add the ``sample=true`` spider argument:

.. code-block:: bash

    scrapy crawl spider_name -a sample=true

Scrapy will then output a log of its activity.

.. _proxy:

Use a proxy
~~~~~~~~~~~

.. note::

   This is an advanced topic. In most cases, you will not need to use this feature.

If the data source is blocking Scrapy's requests, you might need to use a proxy.

To use an HTTP and/or HTTPS proxy, set the ``http_proxy`` and/or ``https_proxy`` environment variables, and `override <https://docs.scrapy.org/en/latest/topics/settings.html#command-line-options>`__ the ``HTTPPROXY_ENABLED`` Scrapy setting:

.. code-block:: bash

    env http_proxy=YOUR-PROXY-URL https_proxy=YOUR-PROXY-URL scrapy crawl spider_name -s HTTPPROXY_ENABLED=True

Use data
--------

You should now have a crawl directory within the ``data`` directory containing OCDS files. For help using data, read about `using open contracting data <https://www.open-contracting.org/data/data-use/>`__.
