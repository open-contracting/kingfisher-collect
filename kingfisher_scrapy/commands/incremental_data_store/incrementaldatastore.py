import datetime
import json
import os

import ijson
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError, NotConfigured

from kingfisher_scrapy import util
from kingfisher_scrapy.commands.incremental_data_store.db import Database

# these can be a command line argument as well
CRAWL_TIME = '2021-04-22T00:00:00'
FOLDER_NAME = datetime.datetime.strptime(CRAWL_TIME, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M%S')
# currently, the command assumes that the given schema exists
SCHEMA_NAME = 'bi'


class IncrementalDataStore(ScrapyCommand):
    def syntax(self):
        return '[options] spider'

    def short_desc(self):
        return 'Store compile releases from the given spider in a PostgresSQL database, incrementally'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--spider', type=str, help='The spider to run')
        parser.add_option('--compile', action='store_true', help='Compile the releases before saving them to the '
                                                                 'database')

    def from_date_formatted(self, last_date, date_format):
        """
        Returns the date formatted as the specified spider date format
        """
        if date_format == 'datetime':
            return last_date[0:19]
        elif date_format == 'date':
            return last_date[0:10]
        elif date_format == 'year-month':
            return last_date[0:7]
        else:
            return last_date[0:6]

    def run_spider(self, last_date, spider_name):

        if not self.settings['FILES_STORE'] or not os.getenv('KINGFISHER_COLLECT_DATABASE_URL'):
            raise NotConfigured('You must set a FILES_STORE and KINGFISHER_COLLECT_DATABASE_URL')

        kwargs = {'crawl_time': CRAWL_TIME}
        spidercls = self.crawler_process.spider_loader.load(spider_name)

        # If there is data already in the database we only download data after the last release date
        if last_date:
            kwargs['from_date'] = self.from_date_formatted(last_date, spidercls.date_format)
        self.crawler_process.crawl(spidercls, **kwargs)
        self.crawler_process.start()

    def run(self, args, opts):
        spiders = self.crawler_process.spider_loader.list()
        spider_name = opts.spider

        if not spider_name or opts.spider not in spiders:
            raise UsageError('A valid spider must be given.')

        # we disable kingfisher process extension
        extensions = {'kingfisher_scrapy.extensions.KingfisherProcessAPI': None}
        self.settings.set('EXTENSIONS', extensions)

        database = Database(SCHEMA_NAME, spider_name)
        last_date = database.get_last_release_date()
        self.run_spider(last_date, spider_name)

        # we drop the table and insert all the data again
        database.re_create_country_table()
        data_directory = os.path.join(self.settings['FILES_STORE'], f'{spider_name}', FOLDER_NAME)
        # if we don't need to compile the releases, we insert them directly in the database
        if opts.compile:
            raise NotImplementedError('The compile option is not implemented yet')
        else:
            for filename in os.listdir(data_directory):
                if filename.endswith('.json'):
                    with open(os.path.join(data_directory, filename)) as f:
                        for item in ijson.items(f, 'releases.item'):
                            database.insert_data_row(json.dumps(item, default=util.default))
            database.commit()
