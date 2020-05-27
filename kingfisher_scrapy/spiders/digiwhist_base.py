import tarfile
from io import BytesIO

from kingfisher_scrapy.base_spider import BaseSpider


class DigiwhistBase(BaseSpider):

    def parse(self, response):
        if response.status == 200:

            yield self.save_response_to_disk(response, 'file.tar.gz', post_to_api=False)

            # Load a line at the time, pass it to API
            with tarfile.open(fileobj=BytesIO(response.body), mode="r:gz") as tar:
                with tar.extractfile(tar.getnames()[0]) as readfp:
                    yield from self.parse_json_lines(readfp, 'release_package', self.start_urls[0])
        else:
            yield self.build_file_error_from_response(response)
