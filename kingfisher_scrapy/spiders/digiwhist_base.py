import tarfile
import json

from kingfisher_scrapy.base_spider import BaseSpider


class DigiwhistBase(BaseSpider):

    def parse(self, response):
        if response.status == 200:

            save_file_name = self.get_local_file_path_including_filestore('file.tar.gz')

            # Save original file
            with open(save_file_name, "wb") as fp:
                fp.write(response.body)

            # Save some extra info alongside that file
            with open(save_file_name + '.fileinfo', 'w') as f:
                f.write(json.dumps({
                    'url': response.request.url,
                    'data_type': 'release_package_json_lines',
                }))

            # Load a line at the time, pass it to API
            number = 0
            with tarfile.open(save_file_name, "r:gz") as tar:
                with tar.extractfile(tar.getnames()[0]) as readfp:
                    line = readfp.readline()
                    while line:
                        number += 1
                        yield {
                            'success': True,
                            'number': number,
                            'file_name': 'data.json',
                            'data': line,
                            'data_type': 'release_package',
                            'url': self.start_urls[0],
                        }
                        line = readfp.readline()
                        if self.is_sample() and number > 10:
                            break

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
