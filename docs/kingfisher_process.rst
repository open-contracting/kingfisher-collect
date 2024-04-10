.. _kingfisher-process:

Integrate with Kingfisher Process
=================================

.. seealso::

   -  :ref:`increment`, about the ``keep_collection_open`` spider argument
   -  :class:`~kingfisher_scrapy.base_spiders.base_spider.BaseSpider`, about the ``ocds_version`` class attribute

Kingfisher Collect has optional integration with `Kingfisher Process <https://kingfisher-process.readthedocs.io/>`__, through the :class:`~kingfisher_scrapy.extensions.kingfisher_process_api2.KingfisherProcessAPI2` extension.

After deploying and starting an instance of Kingfisher Process, set the following either as environment variables or as Scrapy settings in ``kingfisher_scrapy.settings.py``:

``KINGFISHER_API2_URL``
  The URL of Kingfisher Process' web API, for example: ``http://user:pass@localhost:8000``
``RABBIT_URL``
  The URL of the RabbitMQ message broker, for example: ``amqp://user:pass@localhost:5672``
``RABBIT_EXCHANGE_NAME``
  The name of the exchange in RabbitMQ, for example: ``kingfisher_process_development``
``RABBIT_ROUTING_KEY``
  The routing key for messages sent to RabbitMQ, equal to the exchange name with an ``_api`` suffix, for example: ``kingfisher_process_development_api``

Add a note to the collection
----------------------------

Add a note to the ``collection_note`` table in Kingfisher Process. For example, to track provenance:

.. code-block:: bash

   scrapy crawl spider_name -a note='Started by NAME.'

Select which processing steps to run
------------------------------------

Kingfisher Process stores OCDS data, and upgrades it if the spider sets a class attribute of ``ocds_version = '1.0'``. It can also perform the optional steps below.

Run structural checks and create compiled releases
  .. code-block:: bash

     scrapy crawl spider_name -a steps=check,compile
Run structural checks only
  .. code-block:: bash

     scrapy crawl spider_name -a steps=check
Create compiled releases only
  .. code-block:: bash

     scrapy crawl spider_name -a steps=compile
Do neither
  .. code-block:: bash

     scrapy crawl spider_name -a steps=
