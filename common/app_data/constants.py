from dataclasses import dataclass


@dataclass
class FilePath:
    CONFIG = "config.json"


@dataclass
class SmsApiStatus:
    OK: str = "OK"
