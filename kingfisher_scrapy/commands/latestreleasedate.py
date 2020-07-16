import os
from datetime import datetime

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class LatestReleaseDatePerPublisher(ScrapyCommand):
    def short_desc(self):
        return 'Get the latest published release date per publisher'

    def run(self, args, opts):
        # Stop after one item or error.
        self.settings.set('CLOSESPIDER_ERRORCOUNT', 1)
        self.settings.set('CLOSESPIDER_ITEMCOUNT', 1)
        # Limit concurrent requests, to download the minimum.
        self.settings.set('CONCURRENT_REQUESTS', 1)

        # Disable LogStats extension.
        self.settings.set('LOGSTATS_INTERVAL', None)

        path = self.settings['KINGFISHER_LATEST_RELEASE_DATE_FILE_PATH']
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, 'latest_dates.csv')
        if os.path.isfile(filename):
            os.unlink(filename)
        filename = os.path.join(path, 'skipped_spiders.txt')

        runner = CrawlerProcess(settings=self.settings)

        year = datetime.today().year
        with open(filename, 'w') as output:
            for spider_name in runner.spider_loader.list():
                spidercls = runner.spider_loader.load(spider_name)
                if hasattr(spidercls, 'skip_latest_release_date'):
                    output.write(f'Skipping {spider_name}. Reason: {spidercls.skip_latest_release_date}\n')
                else:
                    runner.crawl(spidercls, latest='true', year=year)

        runner.start()
