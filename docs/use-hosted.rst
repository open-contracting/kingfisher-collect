Use - Hosted
============

A hosted version is maintained that you can use if you have access. You can find private details in the CRM.

Scheduling a run
----------------

SSH into the server.

*  Dev: `ssh ocdskfs@ocdskingfisher-dev.default.opendataservices.uk0.bigv.io`
*  Live: `ssh ocdskfs@195.201.163.242`

Then:

.. code-block:: bash

    $ curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=canada_buyandsell
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

To start a sample run:

.. code-block:: bash

    $ curl http://localhost:6800/schedule.json -d project=kingfisher -d spider=canada_buyandsell -d sample=true
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

Run Status
----------

You can see the run status on the Scrapyd web interface. This is at:

*  Dev: http://scrape.ocdskingfisher-dev.default.opendataservices.uk0.bigv.io
*  Live: http://scrape.ocdskingfisher.opendataservices.coop

Because this interface also allows you to carry out operations on the server, you will need a username and password to access it.

Deploying latest spiders
------------------------

Run the sys admin scripts to get the latest version of the code onto the server.

SSH into the server, as above.

*  Change into the folder: `cd ocdskingfisherscrape/`
*  Activate the virtual environment: `source .ve/bin/activate`
*  Deploy: `scrapyd-deploy`
