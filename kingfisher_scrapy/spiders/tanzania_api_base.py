from urllib.parse import parse_qs, urlsplit

import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider


def formatter(url):
    query = parse_qs(urlsplit(url).query)
    # The API omits these parameters from the ``links.next`` URL on the last page of results.
    return "-".join(f"{key}-{query[key][0]}" for key in ("cursor", "since") if query.get(key))


class TanzaniaAPIBase(LinksSpider):
    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # tanzania_bulk_releases

    # LinksSpider
    formatter = staticmethod(formatter)

    async def start(self):
        yield scrapy.Request(
            f"https://nest.go.tz/gateway/nest-data-portal-api/api/{self.data_type.replace('_package', '')}s",
            meta={"file_name": "start.json"},
        )
