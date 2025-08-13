import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid adding duplicate handlers in reload
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(handler)