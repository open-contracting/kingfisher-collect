import enum
import io
import zipfile
from typing import Any

import pydantic
import rarfile

Data = (
    # "in read binary mode, it returns an io.BufferedReader" https://docs.python.org/3/library/functions.html#open
    # https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile
    io.BufferedReader
    # https://rarfile.readthedocs.io/api.html#rarfile.RarFile.open (CompressedFileSpider)
    | rarfile.RarExtFile
    # https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.open (CompressedFileSpider)
    | zipfile.ZipExtFile
    | pydantic.conbytes(strict=True, min_length=1)
    # `dict` behaves better last. https://github.com/open-contracting/kingfisher-collect/issues/995
    | dict
)

base_kwargs = {"validate_assignment": True}


class DataType(str, enum.Enum):
    record = "record"
    release = "release"
    record_package = "record_package"
    release_package = "release_package"


class Resource(pydantic.BaseModel, **base_kwargs):
    file_name: pydantic.constr(strict=True, regex=r"^[^/\\]+$")
    url: pydantic.HttpUrl


class DataResource(Resource, arbitrary_types_allowed=True, use_enum_values=True):
    data_type: DataType
    data: Data
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""

    @pydantic.validator("data", pre=True)  # `pre` is needed to prevent pydantic from type casting
    def check_data(cls, v):
        # pydantic has no `condict()` to set `strict=True` or `min_properties=1`. pydantic/pydantic#1277
        if not isinstance(v, Data | bytes):
            raise AssertionError(f"{type(v).__name__} is not a valid type")  # noqa: TRY004 # false positive
        if not v:
            raise AssertionError("ensure this value is non-empty")
        return v


class File(DataResource):
    pass


# This doesn't inherit from the File class, because we want isinstance(item, File) to be false for FileItem instances.
class FileItem(DataResource):
    number: pydantic.conint(strict=True, gt=0)


class PluckedItem(pydantic.BaseModel, **base_kwargs):
    value: Any
