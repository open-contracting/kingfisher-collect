import os
import tempfile

import rarfile
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.spiders.mexico_nuevo_leon_base import MexicoNuevoLeonBase


class MexicoNuevoLeonReleases(MexicoNuevoLeonBase):
    """
    Bulk download documentation
      https://www.dgcp.gob.do/estandar-mundial-ocds/
    Spider arguments
      sample
        Downloads the co.
    """
    name = 'mexico_nuevo_leon_releases'
    file_name_contains = 'ReleasePackage'
    data_type = 'release_package'
