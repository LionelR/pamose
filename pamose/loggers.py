"""
Logs facilities and registration
"""
import os
import logging


def register(app):

    log_level = app.config.get('LOG_LEVEL', 'WARNING')
    log_format = app.config.get('LOG_FORMAT', '<%(asctime)s> <%(levelname)s> %(message)s')

    if not app.debug:
        from logging.handlers import TimedRotatingFileHandler
        # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
        file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'pamose.log'), 'midnight')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)
    else:
        from logging import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(logging.Formatter(log_format))
        del app.logger.handlers[:]
        app.logger.addHandler(stream_handler)
