from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.base_spider import BaseSpider


def yield_nothing(*args, **kwargs):
    yield


class DryRun(ScrapyCommand):
    def short_desc(self):
        return 'Run a dry run of all spiders'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('-l', '--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                          default='debug', help='The minimum level to log')

    def run(self, args, opts):
        BaseSpider.parse_json_lines = yield_nothing
        BaseSpider.parse_json_array = yield_nothing

        settings = get_project_settings()
        settings.set('LOG_LEVEL', opts.log_level.upper())

        # Stop after one item or error.
        settings.set('CLOSESPIDER_ERRORCOUNT', 1)
        settings.set('CLOSESPIDER_ITEMCOUNT', 1)

        # Disable Kingfisher and Telnet extensions.
        settings.set('EXTENSIONS', {
            'scrapy.extensions.telnet.TelnetConsole': None,
        })

        runner = CrawlerProcess(settings=settings)

        exceptions = {
            # Server unavailable
            'mexico_cdmx',
            # Require authentication
            'openopps',
            'paraguay_dncp_records',
            'paraguay_dncp_releases',
            'paraguay_hacienda',
        }

        for spider_name in runner.spider_loader.list():
            if spider_name not in exceptions:
                spidercls = runner.spider_loader.load(spider_name)
                runner.crawl(spidercls)

        runner.start()
