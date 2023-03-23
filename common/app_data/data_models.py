from pydantic import BaseModel, IPvAnyAddress, Field, FilePath
from common.app_data.enumerations import SmppSystemId


class Config(BaseModel):
    debug_level: str = "INFO"
    http_adapter_address: IPvAnyAddress = "0.0.0.0"
    smpp_gateway_address: IPvAnyAddress = "0.0.0.0"
    smpp_gateway_ip: str
    http_adapter_port: int = Field(default=8000, ge=1024, le=65535)
    smpp_gateway_port: int = Field(default=2775, ge=1024, le=65535)
    sms_gate_smpp_system_id: SmppSystemId = Field(default=SmppSystemId.SV_SMS_GATE, min_length=1, max_length=20)
    http_adapter_smpp_system_id: SmppSystemId = Field(default=SmppSystemId.HTTP_ADAPTER, min_length=1, max_length=20)
    http_adapter_log_path: FilePath
    smpp_gateway_log_path: FilePath


class IncomingSmsMessage(BaseModel):
    sms_from: str
    sms_text: str
    sms_to: str = ""
    sms_date: str = ""
    username: str = ""
