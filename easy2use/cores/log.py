import os
import logging
from logging import config
from logging import handlers


DEFAULT_FORMAT = '%(asctime)s %(process)d %(levelname)s ' \
                 '%(name)s:%(lineno)s %(message)s'


def basic_config(level=logging.INFO, logfmt=DEFAULT_FORMAT, datefmt=None,
                 filename=None, max_mb=None, backup_count=None):
    if filename:
        log_dir = os.path.dirname(filename)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    logging.basicConfig(level=level, filename=filename, format=logfmt,
                        datefmt=datefmt)
    if max_mb:
        handler = handlers.RotatingFileHandler(filename, mode='a',
                                               maxBytes=1024 * 1024 * max_mb,
                                               backupCount=backup_count or 100)
        handler.setFormatter(logging.Formatter(fmt=logfmt, datefmt=datefmt))
        logging.root.handlers[0] = handler


def load_config(config_file):
    config.fileConfig(config_file)


def getLogger(name):
    """
    >>> basic_config(level=logging.DEBUG)
    >>> LOG = getLogger(__name__)
    >>> LOG.debug('debug')
    >>> LOG.info('info' * 100)
    >>> LOG.error('error')
    """
    return logging.getLogger(name)


def get_args():
    from easy2use.cores.cliparser import Argument          # noqa

    return [Argument('-d', '--debug', action='store_true',
                     help='Show debug message'),
            Argument('-v', '--verbose', action='store_true',
                     help='Show verbose message'),
            Argument('--log-file', help='The path of log file'),
            Argument('--max-mb', type=int,
                     help='The max size of log file (units: MB)'),
            Argument('--backup-count', type=int,
                     help='The backup count of log file.'),
            ]


def register_arguments(parser):
    log_group = parser.add_argument_group(title='log arguments')
    for argument in get_args():
        log_group.add_argument(*argument.args, **argument.kwargs)
