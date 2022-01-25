import logging


class MessageLogger:
    def __init__(self):
        return

    @staticmethod
    def configureLogger(csv_file_path, logger_type):
        csv_file_path = csv_file_path
        logger_type = logger_type
        lgr = logging.getLogger(logger_type)
        lgr.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        lgr.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG
        # add a file handler
        fh = logging.FileHandler(csv_file_path)
        fh.setLevel(logging.DEBUG)  # ensure all messages are logged to file

        # create a formatter and set the formatter for the handler.
        frmt = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
        fh.setFormatter(frmt)

        # add the Handler to the logger
        lgr.addHandler(fh)
        print('Finished appending log output to {0}'.format(csv_file_path))
        return lgr


# # create logger
# csv_file_path = r'C:\Users\ksundeen\source\repos\Scripts\SchemaChanges\Scripts\logger.csv'
# logger = MessageLogger.configureLogger(csv_file_path, "Schema Changes")

# # You can now start issuing logging statements in your code
# logger.debug('a debug message')
# logger.info('an info message')
# logger.warn('A Checkout this warning.')
# logger.error('An error writen here.')
# logger.critical('Something very critical happened.')
