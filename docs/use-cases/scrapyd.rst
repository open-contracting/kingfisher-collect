Download data to a remote server
================================

.. note::

   This is an advanced guide, that assumes knowledge of web hosting.

Some spiders take a long time to run (days or weeks), and some data sources have a lot of OCDS data (GBs). In such cases, you might not want to :doc:`local`, and instead use a separate machine. You have two options:

#. Follow the same instructions as :doc:`before<local>`, and start crawls on the other machine
#. Install `Scrapyd <https://scrapyd.readthedocs.io/>`__ on a remote server (this guide)

Install Kingfisher Scrape
-------------------------

On your local machine, :ref:`install Kingfisher Scrape<install>`.

Install Scrapyd
---------------

On the remote server, follow Scrapyd's `installation instructions <https://scrapyd.readthedocs.io/en/stable/install.html>`__, then install the ``requests`` package in the same environment as Scrapyd:

.. code-block:: bash

   pip install requests

Start Scrapyd
-------------

On the remote server, follow Scrapy's `starting instructions <https://scrapyd.readthedocs.io/en/latest/overview.html#starting-scrapyd>`__. Scrapyd should be accessible at ``http://your-remote-server:6800/``. If not, refer to `Scrapyd's documentation <http://scrapyd.readthedocs.org/>`__.

Configure Kingfisher Scrape
---------------------------

Update the ``url`` variable in the ``scrapy.cfg`` file in your ``kingfisher-scrape`` directory, to point to the remote server. By default, the ``scrapy.cfg`` file contains:

.. code-block:: ini

    [deploy]
    url = http://localhost:6800/
    project = kingfisher

You need to at least replace ``localhost``. If you changed the ``http_port`` variable in Scrapyd's `configuration file <https://scrapyd.readthedocs.io/en/stable/config.html>`__, you need to replace ``6800``.

If you changed the ``FILES_STORE`` variable when :ref:`installing Kingfisher Scrape<configure>`, that same directory needs to exist on the remote server, and the ``scrapyd`` process needs permission to write to it. If you are using the default value, then files will be stored in a ``data`` directory under your Scrapyd directory.

Deploy spiders
--------------

On your local machine, deploy the spiders in Kingfisher Scrape to Scrapyd, using the `scrapyd-deploy <https://github.com/scrapy/scrapyd-client/blob/v1.1.0/README.rst>`__ command, which was installed with Kingfisher Scrape:

.. code-block:: bash

    scrapyd-deploy 

Collect data
------------

Schedule a crawl, using `Scrapyd's schedule.json API endpoint <https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json>`__. For example, replace ``localhost`` with your remote server and ``spider_name`` with a spider's name:

.. code-block:: bash

    curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name

If successful, you'll see something like:

.. code-block:: json

    {"status": "ok", "jobid": "6487ec79947edab326d6db28a2d86511e8247444"}

To download only a sample of the available data, add the ``sample=true`` spider argument, :ref:`as before<collect-data>`:

.. code-block:: bash

    curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d sample=true
