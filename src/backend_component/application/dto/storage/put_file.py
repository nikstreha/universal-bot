from dataclasses import dataclass
from typing import BinaryIO

from src.backend_component.application.dto.ai_chat.content_types import ContentTypes


@dataclass(frozen=True)
class PutFileDTO:
    bucket_name: str
    object_name: str
    data: BinaryIO
    content_type: ContentTypes