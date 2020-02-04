Command-line tool
=================

You can use a provided CLI Script. There are various sub-commands.

log-dir-scrape-report
---------------------

This command takes in the path to a directory of log files produced by a Scrapy crawl under Scrapyd.

.. code-block:: shell-session

    python ocdskingfisher-scrape-cli log-dir-scrape-report logs/

For every log file in that directory (ends in ``.log``) it will produce a file with the same name (but ending in ``_report.log``).

It will not produce a report if a report file already exists.

scrape-report
-------------

This command takes in the path to a log file produced by a Scrapy crawl.

.. code-block:: shell-session

    python ocdskingfisher-scrape-cli scrape-report logs/canada_buyandsell/canada_buyandsell.log

It outputs a report on the activity of the crawl to the standard output.
