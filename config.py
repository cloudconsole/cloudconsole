from os.path import abspath, dirname
import logging


APP_DIR = dirname(abspath(__file__))

PORT = 5000

REGIONS = ['us-east-1', 'us-west-1', 'us-west-2', 'eu-west-1']

CRAWLER_PAGE_SIZE = 500

# What datastore do you want to use
# es => elasticserach
DATA_STORE = 'es'
DB_NAME = 'aws'  # Database name

# Elastsearch datastore configuration
ES_NODES = ['localhost']

# log config
LOG_LEVEL = 'DEBUG'

log = logging.getLogger(__name__)
log.setLevel(logging.getLevelName(LOG_LEVEL.upper()))

if LOG_LEVEL.upper() == 'DEBUG':
    formatter = logging.Formatter('%(asctime)s '
                                  '%(levelname)s '
                                  '%(filename)s '
                                  '%(funcName)s '
                                  '%(lineno)d '
                                  '%(name)s '
                                  '%(thread)d '
                                  '%(threadName)s '
                                  '%(message)s ')
else:
    formatter = logging.Formatter('%(asctime)s '
                                  '%(levelname)s '
                                  '%(name)s '
                                  '%(message)s')

# create file handler which logs even debug messages
log_file_handler = logging.FileHandler('/tmp/cloudconsole.log')
log_file_handler.setFormatter(formatter)

log.addHandler(log_file_handler)
