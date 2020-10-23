Contributing
============

There are mainly two types of contributions: **spiders** and **features**.

.. toctree::
   :caption: API reference

   base_spider.rst
   extensions.rst
   util.rst
   exceptions.rst

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
-  Have a look at the :module:`~kingfisher_scrapy.util` module, which contains useful functions, notably :func:`~kingfisher_scrapy.util.handle_http_error`.

After writing the spider, add a docstring for :ref:`spider metadata<spider-metadata>`.

Test the spider
~~~~~~~~~~~~~~~

#. Run the spider with ``scrapy crawl``
#. Check the log for errors and warnings
#. Check whether the data is as expected, in format and number

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

-  Spiders should only yield requests and items, or raise exceptions in `from_crawler <https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.from_crawler>`__.
-  Item pipelines should only modify items, return items, or raise a `DropItem <https://docs.scrapy.org/en/latest/topics/exceptions.html#scrapy.exceptions.DropItem>`__ extension or another exception, in order to clean, validate and filter items.
-  Extensions should only connect signals, typically `item signals <https://docs.scrapy.org/en/latest/topics/signals.html#item-signals>`__ and `spider signals <https://docs.scrapy.org/en/latest/topics/signals.html#spider-signals>`__, in order to write files or send requests to external services like Kingfisher Process.

When using the `Request.meta attribute <https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request.meta>`__, avoid re-using `its special keys <https://docs.scrapy.org/en/latest/topics/request-response.html#topics-request-meta>`__.
