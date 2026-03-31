from dataclasses import dataclass
from typing import BinaryIO

from universal_bot.application.dto.common.content_types import ContentTypes


@dataclass(frozen=True)
class PutFileDTO:
    bucket_name: str
    object_name: str
    data: BinaryIO
    content_type: ContentTypes
