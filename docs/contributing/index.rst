Contributing
============

There are mainly two types of contributions: **spiders** and **features**.

Write a spider
--------------

Learn the data source's access methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Read its API documentation or bulk download documentation. Navigate the API, in your browser or with ``curl``. Inspect its responses, to determine where the OCDS data is located, and whether it includes information like pagination links, total pages or total results.

Choose a base class
~~~~~~~~~~~~~~~~~~~

Access methods for OCDS data are very similar. Spiders therefore share a lot of logic by inheriting from one of the :doc:`base_spider` classes:

-  :class:`~kingfisher_scrapy.base_spider.IndexSpider`: Use if the API includes the total number of results or pages in its response.
-  :class:`~kingfisher_scrapy.base_spider.PeriodicSpider`: Use if the bulk downloads or API methods accept a year or a year and month as a query string parameter or URL path component.
-  :class:`~kingfisher_scrapy.base_spider.LinksSpider`: Use if the API implements `pagination <https://github.com/open-contracting-extensions/ocds_pagination_extension>`__.
-  :class:`~kingfisher_scrapy.base_spider.CompressedFileSpider`: Use if the bulk downloads are ZIP or RAR files.
-  :class:`~kingfisher_scrapy.base_spider.SimpleSpider`: Use in almost all other cases. ``IndexSpider``, ``PeriodicSpider`` and ``LinksSpider`` are child classes of this class.
-  :class:`~kingfisher_scrapy.base_spider.BaseSpider`: All spiders inherit, directly or indirectly, from this class, which in turn inherits from `scrapy.Spider <https://docs.scrapy.org/en/latest/topics/spiders.html>`__. Use if none of the above can be used.

Write the spider
~~~~~~~~~~~~~~~~

After choosing a base class, read its documentation, as well as its parent class' documentation. It's also helpful to read existing spiders that inherit from the same class. A few other pointers:

-  Write different callback methods for different response types. Writing a single callback with many if-else branches to handle different response types is very hard to reason about.
-  The default ``parse`` callback method should be for "leaf" responses: that is, responses that cause no further requests to be yielded, besides pagination requests.
-  Have a look at the :mod:`~kingfisher_scrapy.util` module, which contains useful functions, notably :func:`~kingfisher_scrapy.util.handle_http_error`.

After writing the spider, add a docstring for :ref:`spider metadata<spider-metadata>`.

Since many class attributes that control a spider's behavior, please put the class attributes in this order, including comments with class names:

.. code-block:: python

   class NewSpider(ParentSpider):
      """
      The typical docstring.
      """
      name = 'new_spider'
      # Any other class attributes from Scrapy, including `download_delay`, `download_timeout`, `user_agent`, `custom_settings`

      # BaseSpider
      ocds_version = '1.0'
      date_format = 'datetime'
      default_from_date = '2000-01-01T00:00:00'
      default_until_date = '2010-01-01T00:00:00'
      date_required = True
      unflatten = True
      unflatten_args = {}
      line_delimited = True
      root_path = 'item'
      root_path_max_length = 1
      skip_pluck = 'A reason'

      # SimpleSpider
      data_type = 'release_package'
      encoding = 'iso-8859-1'

      # CompressedFileSpider
      resize_package = True
      file_name_must_contain = '-'

      # LinksSpider
      next_page_formatter = staticmethod(parameters('page'))
      next_pointer = '/next_page/uri'

      # PeriodicSpider
      pattern = 'https://example.com/{}'
      start_requests_callback = 'parse_list'

      # IndexSpider
      total_pages_pointer = '/data/last_page'
      count_pointer = '/meta/count'
      limit = 1000
      use_page = True
      formatter = staticmethod(parameters('pageNumber'))
      param_page = 'pageNumber'
      param_limit = 'customLimit'
      param_offset = = 'customOffset'
      additional_params = {'pageSize': 1000}
      base_url = 'https://example.com/elsewhere'
      yield_list_results = False

Test the spider
~~~~~~~~~~~~~~~

#. Run the spider:

   .. code-block:: bash

      scrapy crawl spider_name

   It can be helpful to write the log to a file:

   .. code-block:: bash

      scrapy crawl spider_name --logfile=debug.log

#. :doc:`Check the log for errors and warnings<../logs>`
#. Check whether the data is as expected, in format and number

Scrapy offers some debugging features that we haven't used yet:

-  `Debugging spiders <https://docs.scrapy.org/en/latest/topics/debug.html>`__
-  `Debugging extensions <https://docs.scrapy.org/en/latest/topics/extensions.html#debugging-extensions>`__
-  `Scrapy shell <https://docs.scrapy.org/en/latest/topics/shell.html>`__
-  `Telnet console <https://docs.scrapy.org/en/latest/topics/telnetconsole.html>`__ for in-progress crawls

Commit the spider
~~~~~~~~~~~~~~~~~

#. Update ``docs/spiders.rst`` with the :ref:`updatedocs` command:

   .. code-block:: bash

      scrapy updatedocs

#. Check the metadata of all spiders,  with the :ref:`checkall` command:

   .. code-block:: bash

      scrapy checkall --loglevel=WARNING

After reviewing the output, you can commit your changes to a branch and make a pull request.

Write a feature
---------------

Learn Scrapy
~~~~~~~~~~~~

Read the `Scrapy documentation <https://docs.scrapy.org/en/latest/>`__. In particular, learn the `data flow and architecture <https://docs.scrapy.org/en/latest/topics/architecture.html>`__. When working on a specific feature, read the relevant documentation, for example:

-  `Spiders <https://docs.scrapy.org/en/latest/topics/spiders.html>`__
-  `Requests and responses <https://docs.scrapy.org/en/latest/topics/request-response.html>`__
-  `Items <https://docs.scrapy.org/en/latest/topics/items.html>`__
-  `Item pipeline <https://docs.scrapy.org/en/latest/topics/item-pipeline.html>`__
-  `Extensions <https://docs.scrapy.org/en/latest/topics/extensions.html>`__ and `signals <https://docs.scrapy.org/en/latest/topics/signals.html>`__
-  `Downloader middleware <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html>`__

The :doc:`../cli` follows the guidance for `running multiple spiders in the same process <https://docs.scrapy.org/en/latest/topics/practices.html#running-multiple-spiders-in-the-same-process>`__.

Use Scrapy
~~~~~~~~~~

The Scrapy framework is very flexible. To maintain a good separation of concerns:

-  A spider's responsibility is to collect *inputs*. It shouldn't perform any slow, blocking operations like writing files. It should only:

   -  Yield requests, to be scheduled by Scrapy's engine
   -  Yield items, to be sent to the item pipeline
   -  Raise a :class:`~kingfisher_scrapy.exceptions.SpiderArgumentError` exception in its `from_crawler <https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.from_crawler>`__ method, if a spider argument is invalid
   -  Raise a :class:`~kingfisher_scrapy.exceptions.MissingEnvVarError` exception in its `from_crawler <https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.from_crawler>`__ method, if a required environment variable isn't set
   -  Raise a :class:`~kingfisher_scrapy.exceptions.AccessTokenError` exception in a request's callback, if the maximum number of attempts to retrieve an access token is reached
   -  Raise any other exception, to be caught by a `spider_error <https://docs.scrapy.org/en/latest/topics/signals.html#spider-error>`__ handler in an extension

-  An item pipeline's responsibility is to clean, validate, filter, modify or substitute items. It should only:

   -  Return an item
   -  Raise a `DropItem <https://docs.scrapy.org/en/latest/topics/exceptions.html#scrapy.exceptions.DropItem>`__ exception, to stop the processing of the item
   -  Raise any other exception, to be caught by an `item_error <https://docs.scrapy.org/en/latest/topics/signals.html#item-error>`__ handler in an extension

-  An extension's responsibility is to write *outputs*: for example, writing files or sending requests to external services like Kingfisher Process. It should only:

   -  Connect signals, typically `item signals <https://docs.scrapy.org/en/latest/topics/signals.html#item-signals>`__ and `spider signals <https://docs.scrapy.org/en/latest/topics/signals.html#spider-signals>`__
   -  Raise a `NotConfigured <https://docs.scrapy.org/en/latest/topics/exceptions.html#notconfigured>`__ exception in its `from_crawler <https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension>`__ method, if a required `setting <https://docs.scrapy.org/en/latest/topics/settings.html>`__ isn't set

-  A downloader middleware's responsibility is to process requests, before they are sent to the internet, and responses, before they are processed by the Spiders. It should only:
   -  Yield a request
   -  Return a Deferred
   -  Yield items

When setting a custom `Request.meta key <https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request.meta>`__, check that the attribute name isn't `already in use <https://docs.scrapy.org/en/latest/topics/request-response.html#topics-request-meta>`__ by Scrapy.

Update requirements
-------------------

Update the requirements files `as documented <https://ocp-software-handbook.readthedocs.io/en/latest/python/applications.html#requirements>`__ in the OCP Software Development Handbook.

Then, re-calculate the checksum for the ``requirements.txt`` file. The checksum is used by deployments to determine whether to update dependencies:

.. code-block:: bash

   shasum -a 256 requirements.txt > requirements.txt.sha256

API reference
-------------

.. toctree::

   base_spider.rst
   extensions.rst
   util.rst
   exceptions.rst
   middlewares.rst
