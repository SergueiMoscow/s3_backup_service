import logging

from api.websocket import socket_manager


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='[%(asctime)s %(msecs)03d] %(module)-10s:%(lineno)3d %(levelname)-7s - %(message)s'
    )


async def log_and_socket(logger, message):
    logger.info(message)
    await socket_manager.send_message(message)
