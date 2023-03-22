from smpplib import gsm, consts
from smpplib.client import Client
from logging import debug
from fastapi import FastAPI
from http import HTTPStatus
from uvicorn import run as run_sms_adapter_api
from common.app_data.constants import FilePath
from common.app_data.data_models import Config, IncomingSmsMessage
from common.app_data.enumerations import SmppSystemId


config: Config = Config.parse_file(FilePath.CONFIG)
fast_api: FastAPI = FastAPI(title="HttpAdapter")
smpp_client: Client = Client(config.smpp_gateway_address, config.smpp_gateway_port)


@fast_api.post("/callback")
def get_smsapi_callback(incoming_sms: IncomingSmsMessage) -> int:
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

    return HTTPStatus.OK


def run_http_adapter():
    smpp_client.set_message_sent_handler(lambda pdu: debug(f"sent {pdu.sequence} {pdu.message_id}"))
    smpp_client.set_message_received_handler(lambda pdu: debug(f"delivered {pdu.receipted_message_id}"))
    smpp_client.connect()
    smpp_client.bind_transmitter(system_id=SmppSystemId.HTTP_ADAPTER)
    run_sms_adapter_api(fast_api, host=config.http_adapter_address, port=config.http_adapter_port)
