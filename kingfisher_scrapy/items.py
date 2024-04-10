from dataclasses import dataclass
from typing import Any


@dataclass
class Item:
    file_name: str
    url: str


@dataclass
class File(Item):
    data_type: str
    data: Any
    # Added by the ValidateJSON middleware, for the Validate pipeline to drop the item if invalid.
    invalid_json: bool = False
    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path: str = ""


# This doesn't inherit from the File class, because we want isinstance(item, File) to be false for FileItem instances.
@dataclass
class FileItem(Item):
    data_type: str
    data: Any
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
    value: Any
