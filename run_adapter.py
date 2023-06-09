from time import sleep
from multiprocessing import Process
from common.app.smpp_gateway import run_smpp_gateway
from common.app.http_adapter import run_http_adapter


if __name__ == "__main__":
    for application in run_smpp_gateway, run_http_adapter:
        application_process = Process(target=application)
        application_process.start()
        sleep(2)  # TODO
