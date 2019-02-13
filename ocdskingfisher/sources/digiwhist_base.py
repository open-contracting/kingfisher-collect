import tarfile

from ocdskingfisher.base import Source
from ocdskingfisher.util import save_content


class DigiwhistBaseSource(Source):
    ignore_release_package_json_lines_missing_releases_error = True

    def gather_all_download_urls(self):
        out = [{
            'url': self.get_data_url(),
            'filename': 'data.jsonlines',
            'data_type': 'release_package_json_lines',
        }]
        return out

    def save_url(self, filename, data, file_path):

        save_content_response = save_content(data['url'], file_path+'-temp.tar.gz', replace_control_codes=False)
        if save_content_response.errors:
            return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

        with tarfile.open(file_path+'-temp.tar.gz', "r:gz") as tar:
            with tar.extractfile(tar.getnames()[0]) as readfp:
                with open(file_path, "wb") as writefp:
                    while True:
                        buf = readfp.read(1024 ^ 2)
                        if buf:
                            writefp.write(buf)
                        else:
                            break

        return self.SaveUrlResult()
