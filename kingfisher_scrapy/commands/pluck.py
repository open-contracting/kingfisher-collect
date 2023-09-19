import json
import logging
import os
from collections import defaultdict

from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError

from kingfisher_scrapy.util import pluck_filename

logger = logging.getLogger(__name__)


class Pluck(ScrapyCommand):
    def short_desc(self):
        return 'Pluck one data value per publisher'

    def syntax(self):
        return '[options] [spider ...]'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_argument('-p', '--package-pointer', dest='pluck_package_pointer',
                            help='The JSON Pointer to the value in the package')
        parser.add_argument('-r', '--release-pointer', dest='pluck_release_pointer',
                            help='The JSON Pointer to the value in the release')
        parser.add_argument('-t', '--truncate', type=int, help='Truncate the value to this number of characters')
        parser.add_argument('--max-bytes', type=int,
                            help='Stop downloading an OCDS file after reading this many bytes')

    def run(self, args, opts):
        if not (bool(opts.pluck_package_pointer) ^ bool(opts.pluck_release_pointer)):
            raise UsageError('Exactly one of --package-pointer or --release-pointer must be set.')

        # Stop after one item or error.
        self.settings.set('CLOSESPIDER_ERRORCOUNT', 1)
        # Disable LogStats extension.
        self.settings.set('LOGSTATS_INTERVAL', None)
        # Disable Telnet extensions.
        self.settings.set('EXTENSIONS', {
            'scrapy.extensions.telnet.TelnetConsole': None,
            'kingfisher_scrapy.extensions.Pluck': 1,
        })
        if opts.max_bytes:
            self.settings.set('KINGFISHER_PLUCK_MAX_BYTES', opts.max_bytes)

        filename = pluck_filename(opts)
        if os.path.isfile(filename):
            os.unlink(filename)

        skipped = defaultdict(list)
        running = []
        for spider_name in self.crawler_process.spider_loader.list():
            if not args or spider_name in args:
                spidercls = self.crawler_process.spider_loader.load(spider_name)
                if not args and hasattr(spidercls, 'skip_pluck'):
                    skipped[spidercls.skip_pluck].append(spider_name)
                else:
                    running.append(spider_name)
                    self.crawler_process.crawl(spidercls, sample=1, package_pointer=opts.pluck_package_pointer,
                                               release_pointer=opts.pluck_release_pointer, truncate=opts.truncate)

        with open('pluck_skipped.json', 'w') as f:
            json.dump(skipped, f, indent=2)

        logger.info('Running %s spiders: %s', len(running), ', '.join(sorted(running)))
        self.crawler_process.start()
