from dataclasses import dataclass
from fastapi.responses import Response


@dataclass
class FilePath:
    CONFIG = "config.json"


@dataclass
class SmsApi:
    STATUS_OK: Response = Response("OK")
    TEST_SMS_SENDER: str = "48900900900"
    TEST_SMS_TEXT: str = "Test message"
