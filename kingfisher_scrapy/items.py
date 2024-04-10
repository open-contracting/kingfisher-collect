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
    # Added by the ValidateJSON middleware, for the Validate pipeline to drop the item if invalid.
    invalid_json: bool = False
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


@dataclass
class FileItem(Item):
    data_type: str
    data: typing.Any
    number: int
    # Added by the ValidateJSON middleware, for the Validate pipeline to drop the item if invalid.
    invalid_json: bool = False
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


@dataclass
class FileError(Item):
    errors: dict


@dataclass
class PluckedItem:
    value: typing.Any
