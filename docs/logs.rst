Log files
=========

You can use Scrapy's log files to identify and debug issues in data collection.

If you can't debug an issue on your own, create an issue on `GitHub <https://github.com/open-contracting/kingfisher-collect/issues>`__.

1. Check for unhandled errors
-----------------------------

Kingfisher Collect can handle errors and continue crawling. This step is to check whether any errors were *unhandled*.

Read the last line of the log file:

.. code-block:: shell

   tail -n 1 logfile.log

If the line looks like:

.. code-block:: none

   2020-01-10 12:34:56 [scrapy.core.engine] INFO: Spider closed (REASON)

Then all errors were handled. Otherwise, either a shutdown was forced (e.g. pressing ``Ctrl-C`` twice), or an error was unhandled. You can read the lines at the end of the file for context:

.. code-block:: shell

   less +G logfile.log

2. Check the reason for closing the spider
------------------------------------------

The last line of the log file (taken above) looked like:

.. code-block:: none

   2020-01-10 12:34:56 [scrapy.core.engine] INFO: Spider closed (REASON)

Reasons implemented by Scrapy's core are:

cancelled
  The spider closed for an unknown reason
finished
  The crawl finished, and any errors were handled
shutdown
  The crawl shutdown gracefully (e.g. pressing ``Ctrl-C`` once)

Reasons implemented by Scrapy's extensions are:

closespider_errorcount
  The spider reached the maximum error count, set by the `CLOSESPIDER_ERRORCOUNT <https://docs.scrapy.org/en/latest/topics/extensions.html#closespider-errorcount>`__ setting (the :ref:`pluck` and :ref:`crawlall` commands set it to 1, otherwise off by default)
closespider_itemcount
  The spider reached the maximum item count, set by the `CLOSESPIDER_ITEMCOUNT <https://docs.scrapy.org/en/latest/topics/extensions.html#closespider-itemcount>`__ setting (off by default)
closespider_pagecount
  The spider reached the maximum page count, set by the `CLOSESPIDER_PAGECOUNT <https://docs.scrapy.org/en/latest/topics/extensions.html#closespider-pagecount>`__ setting (off by default)
closespider_timeout
  The spider remained open longer than the timeout, set by the `CLOSESPIDER_TIMEOUT <https://docs.scrapy.org/en/latest/topics/extensions.html#closespider-timeout>`__ setting (off by default)
memusage_exceeded
  The spider exceeded the maximum allowed memory, set by the `MEMUSAGE_LIMIT_MB <https://docs.scrapy.org/en/latest/topics/settings.html#memusage-limit-mb>`__ setting (off by default)

Reasons implemented by Kingfisher Collect are:

sample
  The crawl reached the maximum sample size, when using the ``sample`` :ref:`spider argument<spider-arguments>`

3. Check the crawl statistics
-----------------------------

Extract the crawl statistics:

.. code-block:: bash

   tac logfile.log | grep -B99 statscollectors | tac

Read the numbers of error messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``log_count/CRITICAL``
-  ``log_count/ERROR``
-  ``log_count/WARNING``

If there are any, filter for and read the messages, for example:

.. code-block:: bash

   grep WARNING logfile.log

..
   Possible messages are found with, for example:
   grep -r ERROR scrapyd/logs/kingfisher | cut -d' ' -f 4-9999 | sort | uniq

   Example exceptions are found with, for example:
   grep -rA30 'ERROR: Spider error processing' scrapyd/logs/kingfisher | grep "log-[A-Za-z]" | grep -v Traceback | cut -d'-' -f 2- | sort | uniq

   Specific examples can be viewed with, for example:
   grep -rA30 'ERROR: Spider error processing' scrapyd/logs/kingfisher | less

Some messages mean that action is needed. The action might be to fix a bug, or to add a try-statement to catch an exception. If you don't know what action is needed, `create an issue <https://github.com/open-contracting/kingfisher-collect/issues>`__ with the name of the spider and an excerpt of the log, including the log message and the full traceback.

CRITICAL: Unhandled error in Deferred:
  An exception was raised before the spider was opened, like :class:`~kingfisher_scrapy.exceptions.SpiderArgumentError`, in which case the problem is in the user's input.
ERROR: Spider error processing <GET https:…> (referer: None)
  An exception was raised in the spider's code. (See the ``spider_exceptions/…`` statistics below.)

  .. attention:: Action needed.

ERROR: Error processing {…}
  An exception was raised in an item pipeline, like ``jsonschema.exceptions.ValidationError``.

  .. attention:: Action needed.

ERROR: Error caught on signal handler: …
  An exception was raised in an extension.

  .. attention:: Action needed.

ERROR: Error downloading <GET https:…>
  An exception was raised by the downloader, typically after failed retries by the `RetryMiddleware <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.retry>`__ downloader middleware. (See the ``downloader/exception_type_count/…`` statistics below.)
WARNING: Failed to post [https:…]. File API status code: 500
  Issued by the :class:`~kingfisher_scrapy.extensions.KingfisherProcessAPI` extension.

  .. admonition:: Potential action

     If you need the collection in Kingfisher Process to be complete, re-run the spider.

WARNING: Dropped: Duplicate File: '….json'
  Issued by the :class:`~kingfisher_scrapy.pipelines.Validate` pipeline.

  .. admonition:: Potential action

     Check whether the key collisions are caused by identical items, or by different items. If by different items, the spider needs to be updated to assign keys without collisions.

WARNING: Got data loss in https:…. If you want to process broken responses set the setting DOWNLOAD_FAIL_ON_DATALOSS = False -- This message won't be shown in further requests
 Issued by Scrapy if the ``Content-Length`` header doesn't match the bytes received, after which Scrapy retries the request. If you don't trust the ``Content-Length`` header, set to ``False`` either the `DOWNLOAD_FAIL_ON_DATALOSS <https://docs.scrapy.org/en/latest/topics/settings.html#download-fail-on-dataloss>`__ key of the spider's `custom_settings <https://docs.scrapy.org/en/latest/topics/settings.html#settings-per-spider>`__ attribute, or the `download_fail_on_dataloss <https://docs.scrapy.org/en/latest/topics/request-response.html#std-reqmeta-download_fail_on_dataloss>`__ key of the request's ``meta`` attribute.
WARNING: Expected response size (987654321) larger than download warn size (123456789) in request <GET https:…>.
  Issued based on the `DOWNLOAD_WARNSIZE <https://docs.scrapy.org/en/latest/topics/settings.html#download-warnsize>`__ setting, ``download_warnsize`` spider attribute or ``download_warnsize`` Request.meta key. Can be ignored.
WARNING: Received more bytes than download warn size (123456789) in request <GET https:…>.
  Issued based on the `DOWNLOAD_WARNSIZE <https://docs.scrapy.org/en/latest/topics/settings.html#download-warnsize>`__ setting, ``download_warnsize`` spider attribute or ``download_warnsize`` Request.meta key. Can be ignored.
WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by '…': …
 Issued by Scrapy's `RetryMiddleware <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.retry>`__ downloader middleware. Can be ignored.

Read the numbers of successful response status codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``downloader/response_status_count/2...``

Decide whether the number is as expected. If the statistic isn't present, there were no successful responses.

Read the numbers of error response status codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``downloader/response_status_count/[4-5]...``

You can look up a `status code's semantics <https://httpstatuses.com/>`__. Decide whether the numbers are elevated.

Some spiders can recover from errors, for example:

-  *401 Unauthorized*: request a new access token
-  *429 Too Many Requests*: back off and retry
-  *503 Service Unavailable*: back off and retry
-  … or try different parameters until a request succeeds

Unrecoverable errors are yielded as FileError items (see :ref:`log-file-error-items`).

Read the numbers of spider exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``spider_exceptions/...``

If there are any, filter for and read the message(s) in which the exception is logged. (See the ``ERROR: Spider error processing`` error message above.)

Read the numbers of downloader exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``downloader/exception_type_count/...``

If there are any, filter for and read the message(s) in which the exception is logged. (See the ``ERROR: Error downloading`` error message above.)

The ``downloader/exception_count`` statistic is the total number of all types of downloader exceptions.

Read the number of requests for which the maximum number of retries was reached
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``retry/max_reached``

The maximum is set by the `RETRY_TIMES <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#std-setting-RETRY_TIMES>`__ setting or the `max_retry_times <https://docs.scrapy.org/en/latest/topics/request-response.html#std-reqmeta-max_retry_times>`__ Request.meta key.

If the maximum is reached, read the exceptions causing retries:

-  ``retry/reason_count/...``

Then, filter for and read the message(s) in which the exception is logged.

.. note::

   The following statistics are not presently collected:

   httperror/response_ignored_count
     Collected if the `HTTPERROR_ALLOW_ALL <https://docs.scrapy.org/en/latest/topics/spider-middleware.html#httperror-allow-all>`__ setting is ``False``.
   scheduler/unserializable
     Collected if the `SCHEDULER_DEBUG <https://docs.scrapy.org/en/latest/topics/settings.html#scheduler-debug>`__ setting is ``True``.

Read the number of duplicate requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``dupefilter/filtered``

Spiders should not send duplicate requests. A duplicate request might indicate a bug in the spider's implementation.

Presently, only the first duplicate request is logged. The line looks like:

.. code-block:: none

   2020-01-10 12:34:56 [scrapy.dupefilters] DEBUG: Filtered duplicate request: <GET http://...> (referer: http://...)

.. _log-file-error-items:

4. Check for FileError items
----------------------------

Kingfisher Collect yields some errors as FileError items. You can open the log file and search for ``'errors':`` to get more context on each error.
