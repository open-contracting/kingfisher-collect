import os
import sys
import json
import datetime
import traceback
import logging

from ocdskingfisher.util import save_content
from ocdskingfisher.metadata_db import MetadataDB

"""Base class for defining OCDS publisher sources.

Each source should extend this class and add some variables and implement a few methods.

method gather_all_download_urls - this is called once at the start and should return a list of files to download.

method save_url - this is called once per file to download. You may not need to implement this for a simple source, as
the default implementation may be good enough. It returns an instance of Source.SaveURLResult which can hold errors,
warnings, and new files to download.

Files to be downloaded are described by a dict. Both gather_all_download_urls and Source.SaveURLResult.additional_files
use the same structure. The keys are:

  *  filename - the name of the file that will be saved locally. These need to be unique per source.
  *  url - the URL to download.
  *  data_type - the type of the file. See below.
  *  encoding - encoding of the file. Optional, defaults to utf-8.
  *  priority - higher numbers will be fetched first, defaults to 1.

The data_type should be one of the following options:

  *  record - the file is a record.
  *  release - the file is a release.
  *  record_package - the file is a record package.
  *  release_package - the file is a release package.
  *  record_package_json_lines - the file is JSON lines, and every line is a record package
  *  release_package_json_lines - see last entry, but release packages.
  *  record_package_list - the file is a list of record packages. eg
     [  { record-package-1 } , { record-package-2 } ]
  *  release_package_list - see last entry, but release packages.
  *  record_package_list_in_results - the file is a list of record packages in the results attribute. eg
     { 'results': [  { record-package-1 } , { record-package-2 } ]  }
  *  release_package_list_in_results - see last entry, but release packages.
  *  meta* - files with a type that starts with meta are fetched as normal, but then ignored while storing to the database.
     You may need these files to work out more files to download. See the ukraine source for an example.
"""


class Source:
    publisher_name = None
    url = None
    output_directory = None
    source_id = None
    sample = False
    data_version = None
    ignore_release_package_json_lines_missing_releases_error = False

    """It is possible to pass extra arguments.

    This specifies a list of the extra arguments possible. Each item in the list should be a dict with the keys:
      *  name - a name compatible with argparse. Names should be unique across all sources, so include a prefix of some kind.
      *  help - a help string for argparse
    """
    argument_definitions = []

    def __init__(self, base_dir, remove_dir=False, publisher_name=None, url=None, sample=False, data_version=None, new_version=False):

        self.base_dir = base_dir
        self.sample = sample

        self.publisher_name = publisher_name or self.publisher_name
        if not self.publisher_name:
            raise AttributeError('A publisher name needs to be specified')

        # Make sure the output directory is fully specified, including sample bit (if applicable)
        self.output_directory = self.output_directory or self.source_id
        if not self.output_directory:
            raise AttributeError('An output directory needs to be specified')

        if self.sample and not self.output_directory.endswith('_sample'):
            self.output_directory += '_sample'

        # Load all versions if possible, pick an existing one or set a new one.
        all_versions = sorted(os.listdir(os.path.join(base_dir, self.output_directory)), reverse=True)\
            if os.path.exists(os.path.join(base_dir, self.output_directory)) else []

        if self.data_version:
            pass
        elif data_version and data_version in all_versions:  # Version specified is valid
            self.data_version = data_version
        elif data_version:   # Version specified is invalid!
            raise AttributeError('A version was specified that does not exist')
        elif new_version or len(all_versions) == 0:  # New Version
            self.data_version = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
        elif len(all_versions) > 0:  # Get the latest version to resume
            self.data_version = all_versions[0]
        else:  # Should not happen...
            raise AttributeError('The version is unavailable on the output directory')

        # Build full directory, make sure it exists
        self.full_directory = os.path.join(base_dir, self.output_directory, self.data_version)

        exists = os.path.exists(self.full_directory)

        try:
            if exists and remove_dir:
                os.rmdir(self.full_directory)
                exists = False

            if not exists:
                os.makedirs(self.full_directory)
        except OSError:
            raise RuntimeError("Error: Write permission is needed on the directory specified (or project dir). %s" % self.full_directory)

        # Misc

        self.url = url or self.url

        self.metadata_db = MetadataDB(self.full_directory)

        self.metadata_db.create_session_metadata(
            publisher_name=self.publisher_name,
            sample=self.sample,
            url=self.url,
            data_version=self.data_version
        )

        self.logger = logging.getLogger('ocdskingfisher.source')

    """Returns an array with objects for each url.

    The return objects includes url,filename,type and more."""
    def gather_all_download_urls(self):
        raise NotImplementedError()

    def set_arguments(self, arguments):
        pass

    def run_gather(self):
        self.logger.info("Starting run_gather")

        metadata = self.metadata_db.get_session()

        if metadata['gather_success']:
            return

        self.metadata_db.update_session_gather_start()

        try:
            for info in self.gather_all_download_urls():
                if self.metadata_db.has_filestatus_filename(info['filename']):
                    if not self.metadata_db.compare_filestatus_to_database(info):
                        raise Exception("Tried to add the file " + info['filename'] +
                                        " but it clashed with a file already in the list!")
                else:
                    self.metadata_db.add_filestatus(info)
        except Exception as e:
            error = repr(e)
            stacktrace = traceback.format_exception(*sys.exc_info())
            self.metadata_db.update_session_gather_end(False, error, stacktrace)
            return

        self.metadata_db.update_session_gather_end(True, None, None)

    def is_gather_finished(self):
        metadata = self.metadata_db.get_session()
        return bool(metadata['gather_finished_datetime'])

    def run_fetch(self):
        self.logger.info("Starting run_fetch")

        metadata = self.metadata_db.get_session()

        if metadata['fetch_success']:
            return

        if not metadata['gather_success']:
            msg = 'Can not run fetch without a successful gather!'
            if metadata['gather_errors']:
                msg += ' Gather errors: ' + metadata['gather_errors']
            raise Exception(msg)

        self.metadata_db.update_session_fetch_start()

        data = self.metadata_db.get_next_filestatus_to_fetch()
        while data:

            self.logger.info("Starting run_fetch for file " + data['filename'])
            self.metadata_db.update_filestatus_fetch_start(data['filename'])
            try:
                response = self.save_url(data['filename'], data, os.path.join(self.full_directory, data['filename']))
                if response.additional_files:
                    for info in response.additional_files:
                        if self.metadata_db.has_filestatus_filename(info['filename']):
                            if not self.metadata_db.compare_filestatus_to_database(info):
                                response.errors.append("Tried to add the file " + info['filename'] +
                                                       " but it clashed with a file already in the list!")
                        else:
                            self.metadata_db.add_filestatus(info)
                self.metadata_db.update_filestatus_fetch_end(data['filename'], response.errors, response.warnings)

            except Exception as e:
                self.metadata_db.update_filestatus_fetch_end(data['filename'], [repr(e)])

            data = self.metadata_db.get_next_filestatus_to_fetch()

        self.metadata_db.update_session_fetch_end()

    def is_fetch_finished(self):
        metadata = self.metadata_db.get_session()
        return bool(metadata['fetch_finished_datetime'])


    def save_url(self, file_name, data, file_path):
        save_content_response = save_content(data['url'], file_path)
        return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

    class SaveUrlResult:
        def __init__(self, additional_files=[], errors=[], warnings=[]):
            self.additional_files = additional_files
            self.errors = errors
            self.warnings = warnings



    """Gather, Fetch, Store and Check data from this publisher."""
    def run_all(self):
        self.run_gather()
        self.run_fetch()


    def force_fetch_to_gather(self):
        self.logger.info("Starting force_fetch_to_gather")
        self.metadata_db.force_fetch_to_gather()
