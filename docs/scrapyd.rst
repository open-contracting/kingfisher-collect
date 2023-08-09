Download data to a remote server
================================

.. note::

   This is an advanced guide that assumes knowledge of web hosting.

Some spiders take a long time to run (days or weeks), and some data sources have a lot of OCDS data (GBs). In such cases, you might not want to :doc:`download data to your computer<local>`, and instead use a separate machine. You have two options:

#. Follow the same instructions as :doc:`before<local>`, and start crawls on the other machine
#. Install `Scrapyd <https://scrapyd.readthedocs.io/>`__ on a remote server (this guide)

Scrapyd also makes it possible for many users to schedule crawls on the same machine.

Install Scrapyd
---------------

On the remote server, follow `these instructions <https://scrapyd.readthedocs.io/en/stable/install.html>`__ to install Scrapyd, then install Kingfisher Collect's requirements in the same environment as Scrapyd:

.. code-block:: bash

   curl -O https://raw.githubusercontent.com/open-contracting/kingfisher-collect/main/requirements.txt
   pip install -r requirements.txt

Start Scrapyd
-------------

On the remote server, follow `these instructions <https://scrapyd.readthedocs.io/en/latest/overview.html#starting-scrapyd>`__ to start Scrapyd. Scrapyd should then be accessible at ``http://your-remote-server:6800/``. If not, refer to `Scrapyd's documentation <http://scrapyd.readthedocs.org/>`__ or its `GitHub issues <https://github.com/scrapy/scrapyd/issues>`__ to troubleshoot.

Using the Scrapyd web interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  To see the scheduled, running and finished crawls, click "Jobs"
-  To browse the crawls' log files, click "Logs"

For help understanding the log files, read :doc:`logs`.

.. note::

   If Scrapyd restarts or the server reboots, all scheduled crawls are cancelled, all running crawls are interrupted, and all finished crawls are delisted from the web interface. However, you can still browse the crawls' logs files to review the finished crawls.

Install Kingfisher Collect
--------------------------

On your local machine, :ref:`install Kingfisher Collect<install>`.

Configure Kingfisher Collect
----------------------------

Create a `~/.config/scrapy.cfg <https://github.com/scrapy/scrapyd-client#targets>`__ file using the template below, and set the ``url`` variable to point to the remote server:

.. code-block:: ini

   [deploy:kingfisher]
   url = http://localhost:6800/
   project = kingfisher

You need to at least replace ``localhost`` with the remote server's domain name. If you changed the ``http_port`` variable in Scrapyd's `configuration file <https://scrapyd.readthedocs.io/en/stable/config.html>`__, you need to replace ``6800``.

If you changed the ``FILES_STORE`` variable when :ref:`installing Kingfisher Collect<configure>`, that same directory needs to exist on the remote server, and the ``scrapyd`` process needs permission to write to it. If you are using the default value, then files will be stored in a ``data`` directory under the Scrapyd directory on the remote server.

Deploy spiders
--------------

On your local machine, deploy the spiders in Kingfisher Collect to Scrapyd, using the `scrapyd-deploy <https://github.com/scrapy/scrapyd-client/blob/v1.1.0/README.rst>`__ command, which was installed with Kingfisher Collect:

.. code-block:: bash

   scrapyd-deploy kingfisher

Remember to run this command every time you add or update a spider.

Collect data
------------

.. note::

   In all examples below, replace ``localhost`` with your remote server's domain name, and replace ``spider_name`` with a spider's name.

You're now ready to collect data!

To list the spiders, use `Scrapyd's listspiders.json API endpoint <https://scrapyd.readthedocs.io/en/stable/api.html#listspiders-json>`__:

.. code-block:: bash

   curl 'http://localhost:6800/listspiders.json?project=kingfisher'

To make the list of spiders easier to read, pipe the response through ``python -m json.tool``:

.. code-block:: bash

   curl 'http://localhost:6800/listspiders.json?project=kingfisher' | python -m json.tool

The spiders' names might be ambiguous. If you're unsure which spider to run, you can find more information about them on the :doc:`spiders` page, or `contact the Data Support Team <data@open-contracting.org>`__.

To run a spider (that is, to schedule a "crawl"), use `Scrapyd's schedule.json API endpoint <https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json>`__:

.. code-block:: bash

   curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name

If successful, you'll see something like:

.. code-block:: json

   {"status": "ok", "jobid": "6487ec79947edab326d6db28a2d86511e8247444"}

To :ref:`download only a sample of the available data<sample>`, :ref:`filter data<filter>` or :ref:`collect data incrementally<increment>`, use ``-d`` instead of ``-a`` before each spider argument:

.. code-block:: bash

   curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d sample=10

To :ref:`use an HTTP and/or HTTPS proxy<proxy>`, `use <https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json>`__ ``-d setting=`` instead of ``-s`` before each overridden setting:

.. code-block:: bash

   curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d setting=HTTPPROXY_ENABLED=True

.. note::

   The ``http_proxy`` and/or ``https_proxy`` environment variables must already be set in Scrapyd's environment on the remote server.

If the crawl's log file contains HTTP 429 Too Many Requests errors, you can make the spider wait between requests by setting the `DOWNLOAD_DELAY <https://docs.scrapy.org/en/latest/topics/settings.html#download-delay>`__ setting (in seconds):

.. code-block:: bash

   curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d setting=DOWNLOAD_DELAY=1
