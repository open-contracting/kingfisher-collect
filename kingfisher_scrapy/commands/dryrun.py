from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess

from kingfisher_scrapy.base_spider import BaseSpider, CompressedFileSpider


def yield_nothing(*args, **kwargs):
    yield


class DryRun(ScrapyCommand):
    def short_desc(self):
        return 'Run a dry run of all spiders'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--sample', type=int, help='The number of sample files to store (default 0)')

    def run(self, args, opts):
        BaseSpider.parse_json_lines = yield_nothing
        CompressedFileSpider.parse = yield_nothing

        # Stop after one item or error.
        self.settings.set('CLOSESPIDER_ERRORCOUNT', 1)
        # Disable LogStats extension.
        self.settings.set('LOGSTATS_INTERVAL', None)

        # Disable custom and Telnet extensions.
        extensions = {'scrapy.extensions.telnet.TelnetConsole': None}
        if opts.sample:
            extensions['kingfisher_scrapy.extensions.KingfisherFilesStore'] = 100

        self.settings.set('EXTENSIONS', extensions)

        runner = CrawlerProcess(settings=self.settings)

        exceptions = {
            'fail',
            # Require authentication
            'openopps',
            'paraguay_dncp_records',
            'paraguay_dncp_releases',
            'paraguay_hacienda',
        }

        for spider_name in runner.spider_loader.list():
            if spider_name not in exceptions:
                spidercls = runner.spider_loader.load(spider_name)
                runner.crawl(spidercls, sample=opts.sample or 1)

        runner.start()
