Download data to your computer
==============================

This page will guide you through installing Kingfisher Collect and using it to collect data from data sources.

.. _install:

Install Kingfisher Collect
--------------------------

To use Kingfisher Collect, you need access to a `Unix-like shell <https://en.wikipedia.org/wiki/Shell_(computing)>`__ (some are available for Windows). `Git <https://git-scm.com>`__ and `Python <https://www.python.org>`__ (version 3.6 or greater) must be installed.

When ready, open a shell, and run:

.. code-block:: bash

   git clone https://github.com/open-contracting/kingfisher-collect.git
   cd kingfisher-collect
   pip install -r requirements.txt

The next steps assume that you have changed to the ``kingfisher-collect`` directory (the ``cd`` command above).

.. _configure:

Configure Kingfisher Collect
----------------------------

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

To download only a sample of the available data, set the sample size with the ``sample`` spider argument:

.. code-block:: bash

    scrapy crawl spider_name -a sample=10

Scrapy will then output a log of its activity.

.. note::

   ``_sample`` will be added to the spider's directory, e.g. ``kingfisher-collect/data/zambia_sample``.

.. _filter:

Filter the data
~~~~~~~~~~~~~~~

Each spider supports different filters, which you can set as spider arguments. For example:

.. code-block:: bash

   scrapy crawl colombia -a from_date=2015-01-01

You can find which filters a spider supports on the :doc:`spiders` page.

Not all of an API's features are exposed by Kingfisher Collect. Each spider links to its API documentation in its :ref:`metadata<spider-metadata>`, where you can learn what filters the API supports. If the filters are implemented as query string parameters, you can apply multiple filters with, for example:

.. code:: bash

    scrapy crawl spider_name -a qs:parameter1=value1 -a qs:parameter2=value2

.. _increment:

Collect data incrementally
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``scrapy crawl`` downloads all the data from the source. You can use :ref:`spider arguments<spider-arguments>` to :ref:`filter the data<filter>`, in order to only collect new data. For example, you might run a first crawl to collect data until yesterday:

.. code-block:: bash

   scrapy crawl spider_name -a until_date=2020-10-14

Then, at a later date, run a second crawl to collect data from the day after until yesterday:

.. code-block:: bash

   scrapy crawl spider_name -a from_date=2020-10-15 -a until_date=2020-10-31

And so on. However, as you learned in :ref:`how-it-works`, each crawl writes data to a separate directory. By default, this directory is named according to the time at which you started the crawl. To collect the incremental data into the same directory, you can take the time from the first crawl's directory name, then override the time of subsequent crawls with the ``crawl_time`` spider argument:

.. code:: bash

    scrapy crawl spider_name -a from_date=2020-10-15 -a until_date=2020-10-31 -a crawl_time=2020-10-14T12:34:56

If you are integrating with :doc:`Kingfisher Process<kingfisher_process>`, remember to set the ``keep_collection_open`` spider argument, in order to not close the collection when the crawl is finished:

.. code:: bash

    scrapy crawl spider_name -a keep_collection_open=true

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
