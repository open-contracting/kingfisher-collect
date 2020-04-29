Crawl Report Guide
==================

A Scrapy crawl is turned into a report. This page has tips on how to interpret this.

HTTP Response Codes
-------------------

Look for a line that tells you how many 200 (Ok) response codes there were.

::

     'downloader/response_status_count/200': 1,

Make sure there are no lines for HTTP codes that were not a 200 status. For example,

::

     'downloader/response_status_count/404': 1,

Note there are times that spiders are able to recover from non-200 errors themselves.

For example, some of the Paraguay spiders need an authentication token. The server may send a 401 or 429 code if there are problems, and the spider can detect that and retry.

This means the presence of a non-200 line is not always a error, but it should always be checked.

Asking for help to interpret problems
-------------------------------------

Unfortunately, it's hard to give clear guides on how to interpret problems as the advice can differ a lot for different spiders.

For hosted Kingfisher, please ask a developer for help with any issues.

If you are running Kingfisher yourself, please open an issue in `GitHub <https://github.com/open-contracting/kingfisher-collect>`_.

In both cases, we will try and build up this documentation as common patterns are uncovered.
