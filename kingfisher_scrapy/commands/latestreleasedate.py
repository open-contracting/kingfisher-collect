import os
import shutil
from datetime import datetime

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class LatestReleaseDatePerPublisher(ScrapyCommand):
    def short_desc(self):
        return 'Get the latest published release date per publisher'

    def run(self, args, opts):
        settings = get_project_settings()
        settings.set('CLOSESPIDER_ITEMCOUNT', 1)
        settings.set('CONCURRENT_REQUESTS', 1)
        settings.set('CLOSESPIDER_ERRORCOUNT', 1)

        process = CrawlerProcess(settings=settings)
        spiders = process.spider_loader.list()
        current_year = datetime.today().year
        filename = get_skipped_output_file(settings)
        with open(filename, 'w') as output:
            for spider in spiders:
                spider_cls = process.spider_loader.load(spider)
                if hasattr(spider_cls, 'skip_latest_release_date'):
                    output.write(f'Skipping {spider}. Reason: {spider_cls.skip_latest_release_date}\n')
                else:
                    process.crawl(spider, latest='true', year=current_year)
        process.start()


def get_skipped_output_file(settings):
    path = settings['KINGFISHER_LATEST_RELEASE_DATE_FILE_PATH']
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, 'skipped_spiders.txt')
