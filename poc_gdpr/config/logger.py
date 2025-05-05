import coloredlogs, logging
coloredlogs.install()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
