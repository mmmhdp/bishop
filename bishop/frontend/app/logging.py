import logging

logger = logging.getLogger('frontend')
logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(
    'frontend.log', maxBytes=1000000, backupCount=5)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
