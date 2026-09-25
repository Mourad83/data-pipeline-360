import logging
from datetime import datetime

from config import LOGS_DIR


def setup_logger():

    LOGS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    log_file = LOGS_DIR / (
        "pipeline_"
        + datetime.now().strftime("%Y%m%d")
        + ".log"
    )

    logger = logging.getLogger(
        "DATA_PIPELINE_360"
    )

    logger.setLevel(
        logging.INFO
    )

    if not logger.handlers:

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

    return logger
