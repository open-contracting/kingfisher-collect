Contributing
============

There are mainly two types of contributions: **spiders** and **features**.

Write a spider
--------------

Learn the data source's access methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Read its API documentation or bulk download documentation. Navigate the API, in your browser or with ``curl``. Inspect its responses, to determine where the OCDS data is located, and whether it includes information like pagination links, total pages or total results.

.. note::

   Please inform the helpdesk analyst of the following, so that it can be reported as feedback to the publisher:
   
   -  If there is no documentation about access methods
   -  If the release package or record package is *not* at the top-level of the JSON data

Choose a spider name
~~~~~~~~~~~~~~~~~~~~

Lowercase and join the components below with underscores. Replace any spaces with underscores.

For an access method to a jurisdiction-specific data source:

-  Country name. Do not use acronyms, like "uk". If in doubt, follow `ISO 3166-1 <https://en.wikipedia.org/wiki/ISO_3166-1>`__. For example: "kyrgyzstan", not "kyrgyz_republic". For a non-country like the European Union, use the relevant geography, like "europe".
-  Subdivision name. Do not use acronyms, like "nsw". Omit the subdivision type, like "state", unless it is typically included, like in `Nigeria <https://en.wikipedia.org/wiki/List_of_Nigerian_states_by_population>`__. If in doubt, follow `ISO 3166-2 <https://en.wikipedia.org/wiki/ISO_3166-2>`__.
-  System name, if needed. Acronyms are allowed, like "ted".
-  Publisher name, if needed. Required if the publisher is not a government.
-  Disambiguator, if needed. For example: "historical".
-  Access method, if needed: "bulk" or "api".
-  OCDS format, if needed: "releases", "records", "release_packages" or "record_packages".

For an access method to a multi-jurisdiction data source:

-  Organization name
-  Disambiguator

If a component repeats another, you can omit or abbreviate the component, like ``peru_compras`` instead of ``peru_peru_compras``.

It is not required for the name to be minimal. For example, ``uganda_releases`` is allowed even if there is no ``uganda_records``.

If you create a new base class, omit the components that are not shared, and add "base" to the end. For example, the ``afghanistan_packages_base.py`` file contains the base class for the ``afghanistan_record_packages`` and ``afghanistan_release_packages`` spiders.

.. note::

   The primary goal is for users to easily find the relevant spider. Keeping the name short and avoiding repetition is a secondary goal. For example, for ``mexico_veracruz_ivai``, the ``v`` in ``ivai`` repeats ``veracruz``, and for ``mexico_mexico_state_infoem``, the ``em`` in ``infoem`` repeats ``mexico_state`` (Estado de México), but abbreviating the ``ivai`` or ``infoem`` acronyms would be less familiar and recognizable to users.

Choose a base class
~~~~~~~~~~~~~~~~~~~

Access methods for OCDS data are very similar. Spiders therefore share a lot of logic by inheriting from one of the :doc:`base_spiders/index`:

-  :class:`~kingfisher_scrapy.base_spiders.index_spider.IndexSpider`: Use if the API includes the total number of results or pages in its response.
-  :class:`~kingfisher_scrapy.base_spiders.periodic_spider.PeriodicSpider`: Use if the bulk downloads or API methods accept a year or a year and month as a query string parameter or URL path component.
-  :class:`~kingfisher_scrapy.base_spiders.links_spider.LinksSpider`: Use if the API implements `pagination <https://github.com/open-contracting-extensions/ocds_pagination_extension>`__.
-  :class:`~kingfisher_scrapy.base_spiders.compressed_file_spider.CompressedFileSpider`: Use if the bulk downloads are ZIP or RAR files.
-  :class:`~kingfisher_scrapy.base_spiders.big_file_spider.BigFileSpider`: Use if the downloads include a big JSON file as a release package that can not be processed in Kingfisher Process.
-  :class:`~kingfisher_scrapy.base_spiders.simple_spider.SimpleSpider`: Use in almost all other cases. ``IndexSpider``, ``PeriodicSpider`` and ``LinksSpider`` are child classes of this class.
-  :class:`~kingfisher_scrapy.base_spiders.base_spider.BaseSpider`: All spiders inherit, directly or indirectly, from this class, which in turn inherits from `scrapy.Spider <https://docs.scrapy.org/en/latest/topics/spiders.html>`__. Use if none of the above can be used.

Write the spider
~~~~~~~~~~~~~~~~

After choosing a base class, read its documentation, as well as its parent class' documentation. It's also helpful to read existing spiders that inherit from the same class. A few other pointers:

-  Write different callback methods for different response types. Writing a single callback with many if-else branches to handle different response types is very hard to reason about.
-  The default ``parse`` callback method should be for "leaf" responses: that is, responses that cause no further requests to be yielded, besides pagination requests.
-  Have a look at the :mod:`~kingfisher_scrapy.util` module, which contains useful functions, notably :func:`~kingfisher_scrapy.util.handle_http_error`.

After writing the spider, add a docstring for :ref:`spider metadata<spider-metadata>`.

.. note::

   If you encountered any challenges, make a note in the *Caveats* section of the spider metadata, and inform the helpdesk analyst, so that it can be reported as feedback to the publisher. Examples:

   -  Requests sometimes fail (e.g. timeout or error), but succeed on retry.
   -  Some requests always fail (e.g. for a specific date).
   -  Error responses are returned with an HTTP 200 status code, instead of a status code in the range 400-599.
   -  The JSON data is encoded as ISO-8859-1, instead of UTF-8 per `RFC 8259 <https://datatracker.ietf.org/doc/html/rfc8259#section-8.1>`__.
   -  The JSON data sometimes contains unescaped newline characters within strings.
   -  The number of results is limited to 10,000.

Since there are many class attributes that control a spider's behavior, please put the class attributes in this order, including comments with class names:

.. code-block:: python

   class NewSpider(ParentSpider):
      """
      The typical docstring.
      """
      name = 'new_spider'
      # Any other class attributes from Scrapy, including `download_delay`, `download_timeout`, `user_agent`, `custom_settings`

      # BaseSpider
      date_format = 'datetime'
      default_from_date = '2000-01-01T00:00:00'
      default_until_date = '2010-01-01T00:00:00'
      date_required = True
      dont_truncate = True
      encoding = 'iso-8859-1'
      concatenated_json = True
      line_delimited = True
      root_path = 'item'
      root_path_max_length = 1
      unflatten = True
      unflatten_args = {}
      ocds_version = '1.0'
      skip_pluck = 'A reason'

      # SimpleSpider
      data_type = 'release_package'

      # CompressedFileSpider
      resize_package = True
      file_name_must_contain = '-'

      # LinksSpider
      formatter = staticmethod(parameters('page'))
      next_pointer = '/next_page/uri'

      # PeriodicSpider
      pattern = 'https://example.com/{}'
      start_requests_callback = 'parse_list'

      # IndexSpider
      total_pages_pointer = '/data/last_page'
      count_pointer = '/meta/count'
      limit = 1000
      use_page = True
      start_page = 0
      formatter = staticmethod(parameters('pageNumber'))
      chronological_order = 'asc'
      parse_list_callback = 'parse_custom'
      param_page = 'pageNumber'
      param_limit = 'customLimit'
      param_offset = = 'customOffset'
      base_url = 'https://example.com/elsewhere'

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
#. Integrate it with :doc:`Kingfisher Process<../kingfisher_process>` and check for errors and warnings in its logs

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
-  `Spider middleware <https://docs.scrapy.org/en/latest/topics/spider-middleware.html>`__

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

-  A downloader middleware's responsibility is to process requests yielded by the spider, before they are sent to the internet, and to process responses from the internet, before they are passed to the spider. It should only:

   -  Return a request, for example :class:`~kingfisher_scrapy.downloadermiddlewares.ParaguayAuthMiddleware`
   -  Return a Deferred, for example :class:`~kingfisher_scrapy.downloadermiddlewares.DelayedRequestMiddleware`

-  A spider middleware's responsibility is to process items yielded by the spider. It should only yield items, for example :class:`~kingfisher_scrapy.spidermiddlewares.RootPathMiddleware`.

-  An item pipeline's responsibility is to clean, validate, filter, modify or substitute items. It should only:

   -  Return an item
   -  Raise a `DropItem <https://docs.scrapy.org/en/latest/topics/exceptions.html#scrapy.exceptions.DropItem>`__ exception, to stop the processing of the item
   -  Raise any other exception, to be caught by an `item_error <https://docs.scrapy.org/en/latest/topics/signals.html#item-error>`__ handler in an extension

-  An extension's responsibility is to write *outputs*: for example, writing files or sending requests to external services like Kingfisher Process. It should only:

   -  Connect signals, typically `item signals <https://docs.scrapy.org/en/latest/topics/signals.html#item-signals>`__ and `spider signals <https://docs.scrapy.org/en/latest/topics/signals.html#spider-signals>`__
   -  Raise a `NotConfigured <https://docs.scrapy.org/en/latest/topics/exceptions.html#notconfigured>`__ exception in its `from_crawler <https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension>`__ method, if a required `setting <https://docs.scrapy.org/en/latest/topics/settings.html>`__ isn't set

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
   base_spiders/index.rst
   downloadermiddlewares.rst
   spidermiddlewares.rst
   pipelines.rst
   extensions.rst
   util.rst
   exceptions.rst
