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

        if os.path.isfile('latestreleasedate.csv'):
            os.unlink('latestreleasedate.csv')

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

        with open('latestreleasedate_skipped.json', 'w') as f:
            json.dump(skipped, f, indent=2)

        runner.start()
