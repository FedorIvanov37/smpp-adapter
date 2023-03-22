from logging import getLevelName, getLogger, Formatter, StreamHandler, Logger as LoggingLogger
from logging.handlers import RotatingFileHandler
from common.app_data.data_models import Config


class Logger:
    def __init__(self, config: Config, output_filename):
        self.config = config
        self.output_filename = output_filename
        self.setup()

    def setup(self):
        logger = getLogger()
        logger.setLevel(getLevelName(self.config.debug_level))
        formatter = Formatter("{asctime} [{levelname}] {message}", "%d-%m-%Y %T", "{")

        file_handler = RotatingFileHandler(
            filename=self.output_filename,
            maxBytes=10 * 1024000,
            backupCount=10,
            encoding="utf-8"
        )

        stream_handler = StreamHandler()

        for handler in file_handler, stream_handler:
            logger.addHandler(handler)
            handler.setFormatter(formatter)

    @staticmethod
    def set_debug_level(level: str):
        if not (logger := getLogger()):
            return

        logger.setLevel(level)
