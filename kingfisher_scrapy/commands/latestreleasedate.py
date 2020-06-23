import os
from datetime import datetime

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from kingfisher_scrapy.spiders.afghanistan_records import AfghanistanRecords
from kingfisher_scrapy.spiders.argentina_vialidad import ArgentinaVialidad
from kingfisher_scrapy.spiders.armenia import Armenia
from kingfisher_scrapy.spiders.australia import Australia
from kingfisher_scrapy.spiders.australia_nsw import AustraliaNSW
from kingfisher_scrapy.spiders.canada_buyandsell import CanadaBuyAndSell
from kingfisher_scrapy.spiders.canada_montreal import CanadaMontreal
from kingfisher_scrapy.spiders.chile_compra_releases import ChileCompraReleases
from kingfisher_scrapy.spiders.colombia import Colombia
from kingfisher_scrapy.spiders.digiwhist_armenia import DigiwhistArmenia


class LatestReleaseDatePerPublisher(ScrapyCommand):
    def short_desc(self):
        return 'Get the latest published release date per publisher'

    def run(self, args, opts):
        settings = get_project_settings()
        settings.set('CLOSESPIDER_ITEMCOUNT', 1)
        settings.set('CONCURRENT_REQUESTS', 1)

        process = CrawlerProcess(settings=settings)
        spiders = process.spider_loader.list()
        path = settings['KINGFISHER_LATEST_RELEASE_DATE_FILE_PATH']
        current_year = datetime.today().year
        if not os.path.exists(path):
            os.makedirs(path)
        filename = os.path.join(path, 'skipped_spiders.txt')
        for spider in spiders:
            spidercls = process.spider_loader.load(spider)
            if hasattr(spidercls, 'skip_latest_release_date'):
                with open(filename, 'a+') as output:
                    output.write('Skipping {} because of {} \n'.format(spider, spidercls.skip_latest_release_date))
            else:
                process.crawl(spider, latest='true', sample='true', year=current_year)
        process.start()
