from enum import Enum


class SmppSystemId(str, Enum):
    def __str__(self):
        return str(self.value)

    SV_SMS_GATE = "sv_sms_gate"
    HTTP_ADAPTER = "http_adapter"
