from json import loads
from smpplib import gsm, consts
from smpplib.client import Client
from logging import debug
from uvicorn import run as run_api
from fastapi import FastAPI, Form, status, HTTPException
from fastapi.responses import Response
from pydantic import ValidationError
from common.app_data.constants import SmsApi
from common.app_data.constants import FilePath
from common.app_data.data_models import Config, IncomingSmsMessage


config: Config = Config.parse_file(FilePath.CONFIG)
fast_api: FastAPI = FastAPI()
smpp_client: Client = Client(config.smpp_address, config.smpp_port)


def run_http_adapter():
    smpp_client.set_message_sent_handler(lambda pdu: debug(f"sent {pdu.sequence} {pdu.message_id}"))
    smpp_client.set_message_received_handler(lambda pdu: debug(f"delivered {pdu.receipted_message_id}"))
    smpp_client.connect()
    smpp_client.bind_transceiver(system_id=config.smpp_sid_http_adapter)
    run_api(fast_api, port=config.http_port, server_header=False)


def process_incoming_message(sms: IncomingSmsMessage) -> Response:
    if sms.sms_from == SmsApi.PING_SMS_SENDER and sms.sms_text == SmsApi.PING_SMS_TEXT:
        return SmsApi.STATUS_OK

    parts, encoding_flag, msg_type_flag = gsm.make_parts(sms.sms_text)

    for part in parts:
        smpp_client.send_message(
            source_addr_ton=consts.SMPP_TON_INTL,
            source_addr=sms.sms_from,
            dest_addr_ton=consts.SMPP_TON_INTL,
            destination_addr=sms.sms_to,
            short_message=part,
            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )

    return SmsApi.STATUS_OK


@fast_api.post("/callback", response_class=Response)
def process_smsapi_callback(
        sms_to: str = Form(),
        sms_from: str = Form(),
        sms_text: str = Form(),
        sms_date: str = Form(),
        username: str = Form(),
):

    try:
        sms: IncomingSmsMessage = IncomingSmsMessage(
            sms_from=sms_from,
            sms_to=sms_to,
            sms_text=sms_text,
            sms_date=sms_date,
            username=username
        )

        response: Response = process_incoming_message(sms)

    except ValidationError as validation_error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=loads(validation_error.json()))

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return response
