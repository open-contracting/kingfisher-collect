Log files
=========

Scrapy log files contain a wealth of information. This page offers ways to quickly extract information from them.

If you can't debug an issue on your own, create an issue on `GitHub <https://github.com/open-contracting/kingfisher-collect/issues>`__.

1. Check for unhandled errors
-----------------------------

Kingfisher Collect can handle errors and continue crawling. This step is to check whether any errors were unhandled.

Read the last line of the log file:

.. code-block:: shell

   tail -n 1 logfile.log

If the line looks like:

.. code-block:: none

   2020-01-10 12:34:56 [scrapy.core.engine] INFO: Spider closed (REASON)

Then all errors were handled. Otherwise, either a shutdown was forced (e.g. pressing ``Ctrl-C`` twice), or an error wasn't handled. You can read the lines at the end of the file for context:

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
  The crawl finished successfully, but not necessarily without errors
shutdown
  The crawl was shutdown gracefully (e.g. pressing ``Ctrl-C`` once)

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
  The crawl reached the maximum sample size, when using the ``sample`` :ref:`spider argument<spider-argument>`

3. Check the crawl statistics
-----------------------------

Extract the crawl statistics:

.. code-block:: bash

   tac logfile.log | grep -B99 statscollectors | tac

Read the number of error messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``log_count/CRITICAL``
-  ``log_count/ERROR``
-  ``log_count/WARNING``

If there are any, filter for and read the messages, for example:

.. code-block:: bash

   grep WARNING logfile.log

Read the number of successful response status codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``downloader/response_status_count/2...``

Decide whether the number is as expected. If no lines are returned, there were no successful responses.

Read the number of error response status codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``downloader/response_status_count/[4-5]...``

Some spiders can recover from errors: for example, 401 Unauthorized or 429 Too Many Requests. You can refer to the semantics of `status codes <https://httpstatuses.com/>`__. Decide whether the numbers are elevated.

Read the number of spider exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``spider_exceptions/...``

If there are any, filter for and read the message(s) in which the exception is logged.

Read the number of downloader exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``downloader/exception_type_count/...``

If there are any, filter for and read the message(s) in which the exception is logged.

The ``downloader/exception_count`` statistic is the total number of all types of downloader exceptions.

Read the number of requests for which the maximum number of retries was reached
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``retry/max_reached``
   
The maximum is set by the `max_retry_times <https://docs.scrapy.org/en/latest/topics/request-response.html#std-reqmeta-max_retry_times>`__ Request.meta attribute or the `RETRY_TIMES <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#std-setting-RETRY_TIMES>`__ setting.

If the maximum is reached, read the exceptions causing retries:

-  ``retry/reason_count/...``

Then, filter for and read the message(s) in which the exception is logged.

.. note::

   The following statistics are not presently collected:

   httperror/response_ignored_count
     Collected if the `HTTPERROR_ALLOW_ALL <https://docs.scrapy.org/en/latest/topics/spider-middleware.html#httperror-allow-all>`__ setting is ``False``.
   scheduler/unserializable
     Collected if the `SCHEDULER_DEBUG <https://docs.scrapy.org/en/latest/topics/settings.html#scheduler-debug>`__ setting is ``True``.

4. Check for FileError items
----------------------------

Kingfisher Collect yields some errors as FileError items. You can open the log file and search for ``'errors':`` to get more context on each error.
