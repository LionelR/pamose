"""
Logs facilities and registration
"""
import os
import logging


def register(app):
    app.logger.debug("Registering loggers...")
    if not app.debug:
        from logging.handlers import TimedRotatingFileHandler
        # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
        file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'pamose.log'), 'midnight')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter('<%(asctime)s> <%(levelname)s> %(message)s'))
        app.logger.addHandler(file_handler)
