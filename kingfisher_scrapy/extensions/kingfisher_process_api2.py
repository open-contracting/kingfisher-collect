import functools
import json
import threading
from urllib.parse import urljoin

import requests
from scrapy import signals
from scrapy.exceptions import NotConfigured
from yapw import methods
from yapw.clients import Async

from kingfisher_scrapy.items import FileError, PluckedItem


class Client(Async):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ready = False

    def exchange_ready(self):
        self.ready = True

    def reset(self):
        super().reset()
        self.ready = False


class KingfisherProcessAPI2:
    """
    If the ``KINGFISHER_API2_URL``, ``RABBIT_URL``, ``RABBIT_EXCHANGE_NAME`` and ``RABBIT_ROUTING_KEY`` environment
    variables or configuration settings are set, then OCDS data is stored in Kingfisher Process, incrementally.

    When the spider is opened, a collection is created in Kingfisher Process via its web API. The API also receives the
    ``note`` and ``steps`` spider arguments (if set) and the spider's ``ocds_version`` class attribute.

    When an item is scraped, a message is published to the exchange for Kingfisher Process in RabbitMQ, with the path
    to the file written by the :class:`~kingfisher_scrapy.extensions.files_store.FilesStore` extension.

    When the spider is closed, the collection is closed in Kingfisher Process via its web API, unless the
    ``keep_collection_open`` spider argument was set to ``'true'``. The API also receives the crawl statistics and the
    reason why the spider was closed.

    .. note::

       If the ``DATABASE_URL`` environment variable or configuration setting is set, this extension is disabled
       and the :class:`~kingfisher_scrapy.extensions.database_store.DatabaseStore` extension is enabled.

    .. note::

       This extension ignores items generated by the :ref:`pluck` command.
    """

    def __init__(self, url, stats, rabbit_url, rabbit_exchange_name, rabbit_routing_key):
        self.url = url
        self.stats = stats
        self.routing_key = rabbit_routing_key
        self.client = Client(url=rabbit_url, exchange=rabbit_exchange_name, routing_key_template="{routing_key}")

        # The collection ID is set by the spider_opened handler.
        self.collection_id = None

    @classmethod
    def from_crawler(cls, crawler):
        url = crawler.settings['KINGFISHER_API2_URL']
        rabbit_url = crawler.settings['RABBIT_URL']
        rabbit_exchange_name = crawler.settings['RABBIT_EXCHANGE_NAME']
        rabbit_routing_key = crawler.settings['RABBIT_ROUTING_KEY']

        if crawler.settings['DATABASE_URL']:
            raise NotConfigured('DATABASE_URL is set.')

        if not url:
            raise NotConfigured('KINGFISHER_API2_URL is not set.')
        if not rabbit_url:
            raise NotConfigured('RABBIT_URL is not set.')
        if not rabbit_exchange_name:
            raise NotConfigured('RABBIT_EXCHANGE_NAME is not set.')
        if not rabbit_routing_key:
            raise NotConfigured('RABBIT_ROUTING_KEY is not set.')

        extension = cls(url, crawler.stats, rabbit_url, rabbit_exchange_name, rabbit_routing_key)
        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider):
        """Send an API request to create a collection in Kingfisher Process."""
        data_version = spider.get_start_time('%Y-%m-%d %H:%M:%S')

        data = {
            'source_id': spider.name,
            'data_version': data_version,
            'sample': bool(spider.sample),
            'upgrade': spider.ocds_version == '1.0',
        }

        if spider.kingfisher_process_note:
            data['note'] = spider.kingfisher_process_note
        if hasattr(spider, '_job'):
            data['job'] = spider._job

        for step in spider.kingfisher_process_steps:
            data[step] = True

        # This request must be synchronous, to have the collection ID for the item_scraped handler.
        response = self._post_synchronous(spider, "/api/collections/", data)

        if response.ok:
            from twisted.internet import reactor

            self.collection_id = response.json()['collection_id']

            # WARNING! If this log message is changed, update the regular expression in the data_registry/
            # process_manager/task/collect.py file in the open-contracting/data-registry repository to match.
            spider.logger.info('Created collection %d in Kingfisher Process (%s)', self.collection_id, data_version)

            # Connect to RabbitMQ only if a collection_id is set, as other signals don't use RabbitMQ, otherwise.
            self.client.connect()

            # threading.Thread(target=cb) is used, instead of reactor.callInThread(cb), because the latter is hard to
            # test. The reactor needs to run for the callback to callInThread() to run. The reactor needs to stop, in
            # order for a test to return. But, the reactor isn't restartable. So, testing seems impossible.
            self.thread = threading.Thread(target=self.client.connection.ioloop.run_forever)
            self.thread.start()

            # Ensure the RabbitMQ connection is closed, if an unclean shutdown is forced.
            reactor.addSystemEventTrigger('before', 'shutdown', self.disconnect_and_join)
        else:
            self._response_error(spider, 'Failed to create collection', response)

    def spider_closed(self, spider, reason):
        """Send an API request to close the collection in Kingfisher Process."""
        if not self.collection_id:
            return

        self.disconnect_and_join()

        if spider.pluck or spider.kingfisher_process_keep_collection_open:
            return

        response = self._post_synchronous(spider, f'/api/collections/{self.collection_id}/close/', {
            'reason': reason,
            'stats': json.loads(json.dumps(self.stats.get_stats(), default=str))  # for datetime objects
        })

        if response.ok:
            spider.logger.info('Closed collection %d in Kingfisher Process', self.collection_id)
        else:
            self._response_error(spider, 'Failed to close collection', response)

    def item_scraped(self, item, spider):
        """Publish a RabbitMQ message to store the file, file item or file error in Kingfisher Process."""
        if not self.collection_id:
            return

        if isinstance(item, PluckedItem):
            return

        data = {
            'collection_id': self.collection_id,
            'url': item.url,
        }

        if isinstance(item, FileError):
            data['errors'] = json.dumps(item.errors)
        else:
            data['path'] = item.path

        cb = functools.partial(self._when_ready, self.client.publish, data, self.routing_key)
        methods.add_callback_threadsafe(self.client.connection, cb)

        # WARNING! Kingfisher Process's API reads this value.
        self.stats.inc_value("kingfisher_process_expected_files_count")

    def disconnect_and_join(self):
        """Close the RabbitMQ connection and join the client's thread."""
        cb = functools.partial(self._when_ready, self.client.interrupt)
        methods.add_callback_threadsafe(self.client.connection, cb)

        # Join last, to avoid blocking before scheduling interrupt.
        self.thread.join()

    def _post_synchronous(self, spider, path, data):
        """POST synchronous API requests to Kingfisher Process."""
        url = urljoin(self.url, path)
        spider.logger.debug('Sending synchronous request to Kingfisher Process at %s with %s', url, data)
        return requests.post(url, json=data, timeout=3600)  # 1h

    def _when_ready(self, function, *args):
        # Scrapy can sometimes reach signals before yapw reaches exchange_ready.
        if self.client.ready:
            function(*args)
        else:
            self.client.connection.ioloop.call_soon(self._when_ready, function, *args)

    def _response_error(self, spider, message, response):
        spider.logger.error('%s: HTTP %d (%s) (%s)', message, response.status_code, response.text, response.headers)
