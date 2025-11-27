import enum
import io
import zipfile
from typing import Annotated, Any

import pydantic
import rarfile
from pydantic import ConfigDict, Field, field_serializer, field_validator

Data = (
    # "in read binary mode, it returns an io.BufferedReader" https://docs.python.org/3/library/functions.html#open
    # https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile
    io.BufferedReader
    # https://rarfile.readthedocs.io/api.html#rarfile.RarFile.open (CompressedFileSpider)
    | rarfile.RarExtFile
    # https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.open (CompressedFileSpider)
    | zipfile.ZipExtFile
    | Annotated[bytes, Field(strict=True, min_length=1)]
    | Annotated[dict, Field(strict=True, min_length=1)]
)


class DataType(str, enum.Enum):
    record = "record"
    release = "release"
    record_package = "record_package"
    release_package = "release_package"


class Resource(pydantic.BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    file_name: Annotated[str, Field(strict=True, pattern=r"^[^/\\]+$")]
    url: pydantic.HttpUrl

    @field_validator("url")
    @classmethod
    def check_url_tld(cls, v):
        if "." not in v.host[1:]:
            raise ValueError("URL must have a valid TLD")
        return v

    @field_serializer("url")
    def serialize_url(self, v, info):
        return str(v)


class DataResource(Resource):
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True, use_enum_values=True)

    data_type: DataType
    data: Data
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


class File(DataResource):
    pass


# This doesn't inherit from the File class, because we want isinstance(item, File) to be false for FileItem instances.
class FileItem(DataResource):
    number: Annotated[int, Field(strict=True, gt=0)]


class PluckedItem(pydantic.BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    value: Any
