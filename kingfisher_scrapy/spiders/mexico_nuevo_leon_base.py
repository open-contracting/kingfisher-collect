import os
import tempfile
from io import BytesIO

import rarfile
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoNuevoLeonBase(BaseSpider):
    """
    Bulk download documentation
      https://www.dgcp.gob.do/estandar-mundial-ocds/
    Spider arguments
      sample
        Downloads the co.
    """
    ocds_type = 'ReleasePackage'

    def start_requests(self):
        yield scrapy.Request(
            'http://si.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar',
            meta={'file_name': 'JSONsInfraestructuraAbierta.rar'}
        )

    def parse(self, response):
        with rarfile.RarFile(BytesIO(response.body)) as tmpfile:
            for f in tmpfile.infolist():
                try:
                    with tmpfile.open(f) as json_file:
                        if self.ocds_type in f.filename:
                            yield self.build_file(file_name=os.path.basename(f.filename), url=response.request.url,
                                                  data=json_file.read(),
                                                  data_type='release_package')
                except TypeError:
                    # the directory doesnt have any files
                    continue
