log-dir-scrape-report
=====================


This command takes in the path to a directory of log files produced by a Scrapy run under Scrapyd.

.. code-block:: shell-session

    python ocdskingfisher-scrape-cli log-dir-scrape-report logs/

For every log file in that directory (ends in ``.log``) it will produce a file with the same name (but ending in ``_report.log``).

It will not produce a report if a report file already exists.

