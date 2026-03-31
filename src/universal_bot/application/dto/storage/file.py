from dataclasses import dataclass
from typing import BinaryIO

from universal_bot.application.dto.common.content_types import ContentTypes


@dataclass(frozen=True)
class FileDTO:
    file_name: str
    data: BinaryIO
    content_type: ContentTypes
