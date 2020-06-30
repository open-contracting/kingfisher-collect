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
        for spider in spiders:
            spider_cls = process.spider_loader.load(spider)
            if hasattr(spider_cls, 'skip_latest_release_date'):
                with open(filename, 'a+') as output:
                    output.write(f'Skipping {spider} because of {spider_cls.skip_latest_release_date} \n')
            else:
                process.crawl(spider, latest='true', year=current_year)
        process.start()


def get_skipped_output_file(settings):
    path = settings['KINGFISHER_LATEST_RELEASE_DATE_FILE_PATH']
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return os.path.join(path, 'skipped_spiders.txt')
