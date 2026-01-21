import logging

LOGGER_NAME = "eventide_python.message_db"


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
