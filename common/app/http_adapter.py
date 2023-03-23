from json import loads
from smpplib import gsm, consts
from smpplib.client import Client
from logging import debug
from fastapi import FastAPI, Form, status, HTTPException
from uvicorn import run as run_api
from common.app_data.constants import FilePath
from common.app_data.data_models import Config, IncomingSmsMessage
from common.app_data.enumerations import SmppSystemId
from pydantic import ValidationError
from common.app_data.constants import SmsApi


config: Config = Config.parse_file(FilePath.CONFIG)
fast_api: FastAPI = FastAPI(title="HttpAdapter")
smpp_client: Client = Client(config.smpp_gateway_ip, config.smpp_gateway_port)


@fast_api.post("/callback")
def get_smsapi_callback(
        sms_to: str = Form(),
        sms_from: str = Form(),
        sms_text: str = Form(),
        sms_date: str = Form(),
        username: str = Form()):

    try:
        incoming_sms = IncomingSmsMessage(
            sms_from=sms_from,
            sms_text=sms_text,
            sms_to=sms_to,
            sms_date=sms_date,
            username=username
        )

    except ValidationError as validation_error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=loads(validation_error.json()))

    if incoming_sms.sms_from == SmsApi.TEST_SMS_SENDER and incoming_sms.sms_text == SmsApi.TEST_SMS_TEXT:
        return SmsApi.STATUS_OK

    parts, encoding_flag, msg_type_flag = gsm.make_parts(incoming_sms.sms_text)

    for part in parts:
        smpp_client.send_message(
            source_addr_ton=consts.SMPP_TON_INTL,
            source_addr=incoming_sms.sms_from,
            dest_addr_ton=consts.SMPP_TON_INTL,
            destination_addr=incoming_sms.sms_to,
            short_message=part,
            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )

    return SmsApi.STATUS_OK


def run_http_adapter():
    smpp_client.set_message_sent_handler(lambda pdu: debug(f"sent {pdu.sequence} {pdu.message_id}"))
    smpp_client.set_message_received_handler(lambda pdu: debug(f"delivered {pdu.receipted_message_id}"))
    smpp_client.connect()
    smpp_client.bind_transceiver(system_id=SmppSystemId.HTTP_ADAPTER)
    run_api(fast_api, host=config.http_adapter_address, port=config.http_adapter_port)
