import json
import logging
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

import pika
import requests
from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.items import FileError, PluckedItem


class KingfisherProcessAPI2:
    """
    If the ``KINGFISHER_API2_URL`` environment variable or configuration setting is set,
    then messages are sent to a Kingfisher Process API for the ``item_scraped`` and ``spider_closed`` signals.
    """

    ITEMS_SENT_POST = 'kingfisher_process_items_sent_post'
    ITEMS_FAILED_POST = 'kingfisher_process_items_failed_post'

    ITEMS_SENT_RABBIT = 'kingfisher_process_items_sent_rabbit'
    ITEMS_FAILED_RABBIT = 'kingfisher_process_items_failed_rabbit'

    def __init__(self, url, stats, rabbit_url, rabbit_exchange_name, rabbit_routing_key):
        self.url = url
        self.stats = stats
        self.exchange = rabbit_exchange_name
        self.routing_key = rabbit_routing_key

        # The collection ID is set by the spider_opened handler.
        self.collection_id = None

        # To avoid DEBUG-level messages from pika
        logging.getLogger('pika').setLevel(logging.WARNING)

        # Add query string parameters to the RabbitMQ URL.
        parsed = urlsplit(rabbit_url)
        query = parse_qs(parsed.query)
        # NOTE: Heartbeat should not be disabled.
        # https://github.com/open-contracting/data-registry/issues/140
        query.update({'blocked_connection_timeout': 1800, 'heartbeat': 0})
        self.rabbit_url = parsed._replace(query=urlencode(query, doseq=True)).geturl()

        self.open_connection_and_channel()
        self.channel.exchange_declare(exchange=self.exchange, durable=True, exchange_type='direct')

    def open_connection_and_channel(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbit_url))
        self.channel = self.connection.channel()

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
        """
        Sends an API request to create a collection in Kingfisher Process.
        """
        data = {
            'source_id': spider.name,
            'data_version': spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            'sample': bool(spider.sample),
            'note': spider.kingfisher_process_note,
            'job': getattr(spider, '_job', None),
            'upgrade': spider.ocds_version == '1.0',
        }

        for step in spider.kingfisher_process_steps:
            data[step] = True

        # This request must be synchronous, to have the collection ID for the item_scraped handler.
        response = self._post_synchronous(spider, 'api/v1/create_collection', data)

        if response.ok:
            self.collection_id = response.json()['collection_id']
            # WARNING! If this log message is changed, then a regular expression in data_registry/cbom/task/scrape.py
            # in the open-contracting/data-registry repository must be updated to match.
            spider.logger.info('Created collection %d in Kingfisher Process', self.collection_id)
        else:
            self._response_error(spider, 'Failed to create collection', response)

    def spider_closed(self, spider, reason):
        """
        Sends an API request to close the collection in Kingfisher Process.
        """
        if spider.pluck or spider.kingfisher_process_keep_collection_open:
            return

        if not self.collection_id:
            return

        response = self._post_synchronous(spider, 'api/v1/close_collection', {
            'collection_id': self.collection_id,
            'reason': reason,
            'stats': json.loads(json.dumps(self.stats.get_stats(), default=str))  # for datetime objects
        })

        if response.ok:
            spider.logger.info('Closed collection %d in Kingfisher Process', self.collection_id)
        else:
            self._response_error(spider, 'Failed to close collection', response)

        self.connection.close()

    def item_scraped(self, item, spider):
        """
        Sends either a RabbitMQ or API request to store the file, file item or file error in Kingfisher Process.
        """
        if isinstance(item, PluckedItem):
            return

        if not self.collection_id:
            return

        data = {
            'collection_id': self.collection_id,
            'url': item['url'],
        }

        if isinstance(item, FileError):
            data['errors'] = json.dumps(item['errors'])
        else:
            data['path'] = item['path']

        for attempt in range(1, 4):
            try:
                self._publish_to_rabbit(data)
            # This error is caused by another error, which might have been caught and logged by pika in another
            # thread: for example, if RabbitMQ crashes due to insufficient memory, the connection is reset.
            except pika.exceptions.ChannelWrongStateError as e:
                spider.logger.warning('Retrying to publish message to RabbitMQ (failed %d times): %s', attempt, e)
                self.open_connection_and_channel()
            except Exception:
                spider.logger.exception('Failed to publish message to RabbitMQ')
                self.stats.inc_value(self.ITEMS_FAILED_RABBIT)
                break
            else:
                self.stats.inc_value(self.ITEMS_SENT_RABBIT)
                break
        else:
            spider.logger.error('Failed to publish message to RabbitMQ (failed 3 times)')
            self.stats.inc_value(self.ITEMS_FAILED_RABBIT)

    def _post_synchronous(self, spider, path, data):
        """
        POSTs synchronous API requests to Kingfisher Process.
        """
        url = urljoin(self.url, path)
        spider.logger.debug('Sending synchronous request to Kingfisher Process at %s with %s', url, data)
        return requests.post(url, json=data)

    # This method is extracted so that it can be mocked in tests.
    def _publish_to_rabbit(self, message):
        # https://www.rabbitmq.com/publishers.html#message-properties
        self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=json.dumps(message),
                                   properties=pika.BasicProperties(delivery_mode=2, content_type='application/json'))

    def _response_error(self, spider, message, response):
        spider.logger.error('%s: HTTP %d (%s) (%s)', message, response.status_code, response.text, response.headers)
