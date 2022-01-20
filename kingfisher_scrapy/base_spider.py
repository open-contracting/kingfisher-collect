import codecs
import os
from datetime import datetime
from io import BytesIO
from math import ceil
from zipfile import ZipFile

import scrapy
from jsonpointer import resolve_pointer
from rarfile import RarFile

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import (IncoherentConfigurationError, MissingNextLinkError, SpiderArgumentError,
                                          UnknownArchiveFormatError)
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.util import (add_path_components, add_query_string, get_file_name_and_extension,
                                    handle_http_error, parameters)




