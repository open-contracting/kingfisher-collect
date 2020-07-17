import json
import os
from collections import defaultdict
from datetime import datetime

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess


class LatestReleaseDatePerPublisher(ScrapyCommand):
    def short_desc(self):
        return 'Get the latest published release date per publisher'

    def run(self, args, opts):
        # Stop after one item or error.
        self.settings.set('CLOSESPIDER_ERRORCOUNT', 1)
        self.settings.set('CLOSESPIDER_ITEMCOUNT', 1)
        # Disable LogStats extension.
        self.settings.set('LOGSTATS_INTERVAL', None)
        # Limit concurrent requests, to download the minimum.
        self.settings.set('CONCURRENT_REQUESTS', 1)

        path = self.settings['KINGFISHER_LATEST_RELEASE_DATE_FILE_PATH']
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, 'dates.csv')
        if os.path.isfile(filename):
            os.unlink(filename)

        runner = CrawlerProcess(settings=self.settings)

        year = datetime.today().year
        skipped = defaultdict(list)
        for spider_name in runner.spider_loader.list():
            if spider_name != 'test_fail':
                spidercls = runner.spider_loader.load(spider_name)
                if hasattr(spidercls, 'skip_latest_release_date'):
                    skipped[spidercls.skip_latest_release_date].append(spider_name)
                else:
                    runner.crawl(spidercls, latest='true', year=year)

        filename = os.path.join(path, 'skipped.json')
        with open(filename, 'w') as f:
            json.dump(skipped, f, indent=2)

        runner.start()
