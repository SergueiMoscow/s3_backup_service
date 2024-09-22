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


def log_vars(file_name, **kwargs):
    """
    Логирует значения переменных в файл.

    :param file_name: Имя файла для записи значений.
    :param kwargs: Переменные для записи в файл.
    """
    with open(file_name, 'a') as log_file:
        for var_name, value in kwargs.items():
            log_file.write(f"{var_name}:\n")

            if isinstance(value, (list, tuple)):
                for item in value:
                    log_file.write(f"  - {item}\n")
            elif isinstance(value, dict):
                for key, val in value.items():
                    log_file.write(f"  {key}: {val}\n")
            else:
                log_file.write(f"  {value}\n")

            log_file.write("\n")
