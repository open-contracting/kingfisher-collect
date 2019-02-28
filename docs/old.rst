Old Spiders
-----------

Same sources only have spiders written in the old system. These do not use Scrapy. This system is available in this repository, but over time all scrapers will be ported to Scrapy and this old system will be removed.

Configuration
=============

Create the file ~/.config/ocdskingfisher/old-config.ini


.. code-block:: ini

    ; sample_ocdsdata_config.ini

    [DATA]
    DIR = /var/ocdskingfisher/data

    [SERVER]
    URL=http://localhost:9090
    API_KEY=key_goes_here

The `data` section sets the place where files are stored on disk, and the `server` sets the Process app it posts the data to.

Running a scraper
=================

Run it by passing the name of a source to run:

.. code-block:: shell-session

    python ocdskingfisher-old-cli run --note="Started by Fred." taiwan
    python ocdskingfisher-old-cli run --note="Started by Fred." digiwhist_armenia

There is a sample mode. This only fetches a small amount of data for each source.

.. code-block:: shell-session

    python ocdskingfisher-old-cli run --note="Started by Fred." --sample taiwan

Update the note with your name, and anything else of interest.

It will look for existing collections with the same source and sample flag as you specify, and by default resume the latest one.

To make sure you start a new collection, pass the `newversion` flag.

.. code-block:: shell-session

    python ocdskingfisher-old-cli run --newversion  taiwan

To select an existing collection, pass the `dataversion` flag.

.. code-block:: shell-session

    python ocdskingfisher-old-cli run --dataversion 2018-07-31-16-03-50 taiwan



