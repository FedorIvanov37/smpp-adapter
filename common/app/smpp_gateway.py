from logging import getLogger, debug
from asyncio import get_event_loop
from smppy.server import SmppClient, Application
from common.app_data.data_models import Config
from common.app_data.constants import FilePath


class SmppGateway(Application):
    sv_sms_gate_client: SmppClient | None = None

    def __init__(self, name: str, logger):
        super(SmppGateway, self).__init__(name=name, logger=logger)
        self.config = Config.parse_file(FilePath.CONFIG)

    async def handle_bound_client(self, client: SmppClient) -> SmppClient:
        self.logger.debug(f"Smpp client {client.system_id} connected")

        if client.system_id not in (self.config.smpp_sid_http_adapter, self.config.smpp_sid_sms_gate):
            raise NameError(f"Unknown smpp client system id: {client.system_id}")

        if client.system_id == self.config.smpp_sid_sms_gate:
            self.sv_sms_gate_client = client

        return client

    async def handle_unbound_client(self, client: SmppClient):
        debug(f"Client {client.system_id} disconnected")

    async def handle_sms_received(self, client: SmppClient, source_number: str, dest_number: str, text: str):
        self.logger.debug(f'Received {text} from {source_number}')

        if self.sv_sms_gate_client is None:
            return

        await self.sv_sms_gate_client.send_sms(dest=dest_number, source=source_number, text=text)


def run_smpp_gateway():
    config: Config = Config.parse_file(FilePath.CONFIG)
    event_loop = get_event_loop()
    smpp_gateway: SmppGateway = SmppGateway(name='smpp_gateway', logger=getLogger('smpp_gateway'))
    smpp_gateway.run(loop=event_loop, port=config.smpp_port)
