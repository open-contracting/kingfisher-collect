import typing
from dataclasses import dataclass


@dataclass
class Item:
    file_name: str
    url: str


@dataclass
class File(Item):
    data_type: str
    data: typing.Any
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""
    # Added by the CheckJSONFormat middleware, for the Validate pipeline to drop the item if invalid.
    invalid_format: bool = False


@dataclass
class FileItem(Item):
    data_type: str
    data: typing.Any
    number: int
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""
    # Added by the CheckJSONFormat middleware, for the Validate pipeline to drop the item if invalid.
    invalid_format: bool = False


@dataclass
class FileError(Item):
    errors: dict


@dataclass
class PluckedItem:
    value: typing.Any
