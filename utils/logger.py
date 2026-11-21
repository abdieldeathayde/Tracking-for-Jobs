import logging
from logging.handlers import RotatingFileHandler

from jobapply.config import LOG_DIR


def get_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("jobapply")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(
            LOG_DIR / "jobapply.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger