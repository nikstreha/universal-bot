from enum import Enum


class ContentTypes(str, Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    WEBP = "image/webp"
    PDF = "application/pdf"
