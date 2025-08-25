import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FILE_PATH = Path("prod_logs.log").resolve()


def configure_logging() -> logging.Logger:
	"""Configure root logger for the Booking Services API.

	- Logs to console and a rotating file (prod_logs.log)
	- Uses a structured, single-line formatter with ISO timestamps
	"""
	logger = logging.getLogger("BookingServicesAPI")
	if logger.handlers:
		# Already configured
		return logger

	logger.setLevel(logging.INFO)

	# Ensure directory exists
	LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

	formatter = logging.Formatter(
		fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
		datefmt="%Y-%m-%dT%H:%M:%S.%fZ",
	)

	# File handler with rotation
	file_handler = RotatingFileHandler(
		LOG_FILE_PATH,
		maxBytes=5 * 1024 * 1024,  # 5 MB
		backupCount=5,
		encoding="utf-8",
	)
	file_handler.setFormatter(formatter)
	file_handler.setLevel(logging.INFO)

	# Console handler
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	console_handler.setLevel(logging.INFO)

	logger.addHandler(file_handler)
	logger.addHandler(console_handler)

	# Reduce noise from third-party libs if needed
	logging.getLogger("uvicorn").setLevel(logging.WARNING)
	logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
	logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

	return logger


