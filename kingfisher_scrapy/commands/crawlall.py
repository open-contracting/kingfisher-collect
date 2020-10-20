from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import UsageError

from kingfisher_scrapy.base_spider import BaseSpider, CompressedFileSpider

EXCEPTIONS = {
    'fail',
    # Require authentication
    'openopps',
    'paraguay_dncp_records',
    'paraguay_dncp_releases',
    'paraguay_hacienda',
}


def yield_nothing(*args, **kwargs):
    yield


class CrawlAll(ScrapyCommand):
    def short_desc(self):
        return 'Run all spiders'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--dry-run', action='store_true', help='Runs the spiders without writing any files')
        parser.add_option('--sample', type=int, help='The number of files to write')

    def run(self, args, opts):
        if opts.sample and opts.dry_run:
            raise UsageError('You cannot specify both --dry-run and --sample.')
        if opts.sample is not None and opts.sample <= 0:
            raise UsageError('--sample must be a positive integer.')

        kwargs = {}
        extensions = {'scrapy.extensions.telnet.TelnetConsole': None}

        if opts.sample:
            kwargs['sample'] = opts.sample

        if opts.dry_run:
            kwargs['sample'] = 1
        else:
            extensions['kingfisher_scrapy.extensions.KingfisherFilesStore'] = 100

        BaseSpider.parse_json_lines = yield_nothing
        CompressedFileSpider.parse = yield_nothing

        # Stop after one item or error.
        self.settings.set('CLOSESPIDER_ERRORCOUNT', 1)
        # Disable LogStats extension.
        self.settings.set('LOGSTATS_INTERVAL', None)
        # Disable custom and Telnet extensions.
        self.settings.set('EXTENSIONS', extensions)

        runner = CrawlerProcess(settings=self.settings)

        for spider_name in runner.spider_loader.list():
            if spider_name not in EXCEPTIONS:
                spidercls = runner.spider_loader.load(spider_name)
                runner.crawl(spidercls, **kwargs)

        runner.start()
