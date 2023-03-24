from pydantic import BaseModel, Field, FilePath


class Config(BaseModel):
    debug_level: str = "INFO"
    smpp_address: str
    http_port: int = Field(default=8000, ge=1024, le=65536)
    smpp_port: int = Field(default=2775, ge=1024, le=65536)
    smpp_sid_sms_gate: str = Field(..., min_length=1, max_length=20)
    smpp_sid_http_adapter: str = Field(..., min_length=1, max_length=20)
    http_log_path: FilePath
    smpp_log_path: FilePath


class IncomingSmsMessage(BaseModel):
    sms_from: str
    sms_text: str
    sms_to: str
    sms_date: float
    username: str
