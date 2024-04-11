from dataclasses import dataclass
from typing import Any


@dataclass
class Item:
    file_name: str
    url: str


# data can be: bytes | dict | list | io.BufferedReader | rarfile.RarExtFile | zipfile.ZipExtFile
@dataclass
class File(Item):
    data_type: str
    data: Any
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


# This doesn't inherit from the File class, because we want isinstance(item, File) to be false for FileItem instances.
@dataclass
class FileItem(Item):
    data_type: str
    data: Any
    number: int
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


@dataclass
class FileError(Item):
    errors: dict


@dataclass
class PluckedItem:
    value: Any
