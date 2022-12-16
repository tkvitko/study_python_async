# import logging
# import os
# from logging import handlers
#
# LOG_DIR = 'logs'
# log_format = logging.Formatter('%(asctime)s %(module)s %(levelname)s %(message)s')
# server_log_handler = handlers.TimedRotatingFileHandler(filename=os.path.join(LOG_DIR, 'server.log'),
#                                                        when='D',
#                                                        interval=1,
#                                                        backupCount=2)
# # server_log_handler = logging.FileHandler('server_file.log')
# server_log_handler.setFormatter(log_format)
#
# server_log = logging.getLogger('server')
# server_log.setLevel(logging.INFO)
# server_log.addHandler(server_log_handler)
