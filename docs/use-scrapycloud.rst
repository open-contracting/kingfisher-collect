Use - Scrapy Cloud (on Scrapinghub)
===================================

Configure Scrapy Cloud
------------------------

You will need an account on Scrapinghub.com, and to create a project in the Scrapy cloud.

You can create a test project for free in your user account (not an organisation).


Configure Local Scripts
-----------------------

Install the ``shub`` package.

.. code-block:: bash

  pip3 install shub

Login to shub

.. code-block:: bash

  shub login

Edit scrapinghub.yml and set the id of the project you want to use.


Deploying Scrapers
------------------

The code must be packaged up and deployed to the server

.. code-block:: bash

    shub deploy


Scheduling a run
----------------

Do this from the web interface.

To schedule a sample run, when you click run you can add arguments. Add one with the name of "sample" and the value of "true".

Output - Disk
-------------

TODO

Output - Kingfisher Process
---------------------------

Make sure ``ITEM_PIPELINES`` includes ``KingfisherFilesPipeline`` and ``KingfisherPostPipeline``,
that ``FILES_STORE`` is set and that the 3 API variables are set to load from the environment. For example:

.. code-block:: python

    ITEM_PIPELINES = {
        'kingfisher_scrapy.pipelines.KingfisherFilesPipeline': 2,
        'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 3,
    }

    FILES_STORE = 'data'

    KINGFISHER_API_FILE_URI = os.environ.get('KINGFISHER_API_FILE_URI')
    KINGFISHER_API_ITEM_URI = os.environ.get('KINGFISHER_API_ITEM_URI')
    KINGFISHER_API_KEY = os.environ.get('KINGFISHER_API_KEY')


The ``kingfisher-process`` API endpoint variables are currently accessed from the Scrapy Cloud environment.
To configure these, go to the Scrapy Cloud project and select "Spiders" and "Settings" from the left menu.
Add the options under the "Raw Settings" tab. The format is:

.. code-block:: text

    KINGFISHER_API_FILE_URI = https://kingfisher.example/api/v1/submit/file/
    KINGFISHER_API_ITEM_URI = https://kingfisher.example/api/v1/submit/item/
    KINGFISHER_API_KEY = api-key-here


