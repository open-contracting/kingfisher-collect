Use - Hosted Kingfisher
=======================

A hosted version of kingfisher-scrape is maintained by OCP for internal use. If you require access but don't have it, contact Open Data Services Co-Op.

Downloading Data
----------------

Kingfisher uses the Scrapy framework to download data from published sources. Hosted Kingfisher uses the scrapyd server in order to manage work from multiple users at once. Instead of running a single command to start a download, users issue a command to the scrapyd server to put a crawl job in the queue. This is called 'scheduling a crawl'. Once a crawl has been scheduled, users can check on its status via a web UI.


Scheduling a Crawl
------------------

First, SSH into the server. For access details, see the `hosted kingfisher documentation <https://ocdskingfisher.readthedocs.io/en/latest/#hosted-kingfisher>`_

Then, for example, replacing ``spider_name`` with a spider's name like ``canada_buyandsell`` and ``NAME`` with your name:

.. code-block:: bash

    $ curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d note="Started by NAME."

Update the note with anything else of interest.

If successful, you should see output that looks like:

.. code-block:: bash

   {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}
    
To start a crawl using 'sample mode', to obtain a small amount of data quickly, add ``-d sample-true``, for example:

.. code-block:: bash

    $ curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=spider_name -d note="Started by NAME." -d sample=true
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

Scheduling a Crawl using a proxy
--------------------------------

Some spiders can use a proxy. To do this, use the commands above but add the the https_proxy and http_proxy options.

.. code-block:: bash

    $ ... -d https_proxy=URL -d http_proxy=URL

Note only some spiders will make use of a proxy. Other spiders will silently ignore these options.


Crawl Status & Logs
-------------------

You can see the crawl status on the `Scrapyd web interface <http://scrape.kingfisher.open-contracting.org>`_. The username and password can be supplied by Open Data Services Co-op on request.

If Scrapyd has been restarted, the jobs will be cleared from the web interface. But the logs are still available on the server - SSH in and see `/home/ocdskfs/scrapyd/logs/kingfisher`. You can also browse `the Scrapyd logs interface <http://scrape.kingfisher.open-contracting.org/logs/>`_.

There is also a summary report generated for each crawl. These are generated a short while after the crawl has finished, so you may have to wait for these.

To find them, navigate `the Scrapyd logs interface <http://scrape.kingfisher.open-contracting.org/logs/>`_ and look for file names with `_report` in.

If you are on the `the Scrapyd jobs interface <http://scrape.kingfisher.open-contracting.org/jobs>`_ and want to see the report for a run that has finished:

* Right click on the link to the log.
* Select Copy Link Location, or similar.
* Paste the link into the address bar.
* Change `.log` at the end to `_report.log` and press enter to load the new URL.

Deploying Latest Spiders
------------------------

If you've developed a new spider (or made updates to an existing one), then you should ensure that they have been merged to the master branch of the kingfisher-scrape repo. 

SSH into the server, as above, then:

*  Change into the folder: `cd ocdskingfisherscrape/`
*  Make sure the code is the latest version of the master branch: `git pull`
*  Activate the virtual environment: `source .ve/bin/activate`
*  Update the virtual environment: `pip3 install -r requirements.txt`
*  Deploy: `scrapyd-deploy`

(Sometimes, it may be necessary to use salt to get the latest version of the code onto the server and update the server to the correct configuration. Most of the time this isn't needed though, and you can just use git as described here. If you're not set up for this (or have no idea what this means!), speak to the Open Data Services development team.)

Are any spiders currently running?
----------------------------------

You may want to know this before doing server maintenance, stopping or starting Scrapyd, etc.

For spiders in Scrapy, check the `Scrapyd web interface <http://scrape.kingfisher.open-contracting.org>`_ - click on `Jobs` and look in the `Running` section.
