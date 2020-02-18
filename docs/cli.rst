Command-line tools
==================

scrape-report
-------------

Extracts the Scrapy statistics from a crawl's log file.

.. code-block:: bash

    python ocdskingfisher-scrape-cli scrape-report scrapyd/logs/kingfisher/spider_name/6487ec79947edab326d6db28a2d86511.log

This is essentially the same as:

.. code-block:: bash

    tac ../scrapyd/logs/kingfisher/spider_name/6487ec79947edab326d6db28a2d86511.log | grep -B99 statscollectors | tac

log-dir-scrape-report
---------------------

Extracts the Scrapy statistics from each crawl's log file, and writes them to a new ``*_report.log`` file.

.. code-block:: bash

    python ocdskingfisher-scrape-cli log-dir-scrape-report scrapyd/logs/

This is essentially the same as:

.. code-block:: bash

    find ../scrapyd/logs/ -type f -name "*.log" -not -name "*_report.log" -exec sh -c 'if [ ! -f {}.stats ]; then result=$(tac {} | head -n99 | grep -m1 -B99 statscollectors | tac); if [ ! -z "$result" ]; then echo "$result" > {}.stats; fi; fi' \;
