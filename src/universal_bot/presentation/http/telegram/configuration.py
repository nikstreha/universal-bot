from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class WebhookConfiguration:
    secret: str = field(repr=False)
    enabled: bool = True
    max_body_bytes: int = 1024 * 1024
