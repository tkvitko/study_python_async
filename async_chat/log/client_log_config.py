import logging
import os
from logging import handlers

LOG_DIR = 'logs'

log_format = logging.Formatter('%(asctime)s %(module)s %(levelname)s %(message)s')
client_log_handler = handlers.TimedRotatingFileHandler(filename=os.path.join(LOG_DIR, 'client.log'),
                                                       when='D',
                                                       interval=1,
                                                       backupCount=2)
client_log_handler.setFormatter(log_format)

client_log = logging.getLogger('client')
client_log.setLevel(logging.INFO)
client_log.addHandler(client_log_handler)
