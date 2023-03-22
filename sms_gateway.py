import logging
import sys
import smpplib.gsm
import smpplib.consts
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads


class SmsAdapter(BaseHTTPRequestHandler):
    smpp_client = smpplib.client.Client('192.168.1.94', 2775, allow_unknown_opt_params=True)
    smpp_client.set_message_sent_handler(lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
    smpp_client.set_message_received_handler(lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))
    smpp_client.connect()
    smpp_client.bind_transceiver()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        incoming_message = self.rfile.read(content_length).decode()
        self.process_incoming_message(incoming_message)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b"{}")

    def process_incoming_message(self, sms_message):
        sms_message: dict[str, str] = loads(sms_message)
        sms_from = sms_message.get("sms_from")
        sms_text = sms_message.get("sms_text")

        parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(sms_text)

        for part in parts:
            self.smpp_client.send_message(
                source_addr_ton=smpplib.consts.SMPP_TON_INTL,
                source_addr=sms_from,
                dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                destination_addr='UNLIMINT',
                short_message=part,
                data_coding=encoding_flag,
                esm_class=msg_type_flag,
                registered_delivery=True,
            )


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    with HTTPServer(('0.0.0.0', 8000), SmsAdapter) as server:
        server.serve_forever()
