import enum
from typing import Any, TypedDict

import pydantic

"""
data can be:

-  bytes
-  dict
-  list
- `zipfile.ZipExtFile <https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.open>`__ (CompressedFileSpider)
- `rarfile.RarExtFile <https://rarfile.readthedocs.io/api.html#rarfile.RarFile.open>`__ (CompressedFileSpider)
- `io.BufferedReader <https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile>`__ (DigiwhistBase)

However, there is either a bug or an issue in pydantic.
https://github.com/open-contracting/kingfisher-collect/issues/995#issuecomment-2048905528

`Any` allows None, as Python has no way to say "not None".
https://github.com/python/typing/issues/801
"""

kwargs = {'use_enum_values': True, 'validate_assignment': True}


class DataType(str, enum.Enum):
    record = "record"
    release = "release"
    record_package = "record_package"
    release_package = "release_package"


class Errors(TypedDict):
    http_code: pydantic.conint(strict=True, ge=100, lt=600)


class Item(pydantic.BaseModel):
    file_name: pydantic.constr(strict=True, regex=r'^[^/]+$')  # noqa: F722 pydantic/pydantic#2872
    url: pydantic.HttpUrl


class File(Item, **kwargs):
    data_type: DataType
    data: Any
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


# This doesn't inherit from the File class, because we want isinstance(item, File) to be false for FileItem instances.
class FileItem(Item, **kwargs):
    data_type: DataType
    data: Any
    number: pydantic.conint(strict=True, gt=0)
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


class FileError(Item):
    errors: Errors


class PluckedItem(pydantic.BaseModel):
    value: Any
