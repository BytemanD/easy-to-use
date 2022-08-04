import os
import logging
from logging import config
from logging import handlers

from easy2use import date
from easy2use.globals.cli import Arg
from easy2use.globals.cli import ArgGroup

FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s:%(lineno)s ' \
         '%(message)s'
FORMAT_EXTRA = '%(asctime)s %(process)d %(levelname)s %(name)s:%(lineno)s' \
               '%(extras)s %(message)s'
DATE_FMT = date.YMD_HMS
BACKUP_COUNT = 10

LOG_ARGS = [Arg('-d', '--debug', action='store_true',
                help='Show debug message'),
            Arg('-v', '--verbose', action='store_true',
                help='Show verbose message'),
            Arg('--log-file', help='The path of log file'),
            Arg('--max-mb', type=int,
                help='The max size of log file (units: MB)'),
            Arg('--backup-count', type=int, default=BACKUP_COUNT,
                help=f'The backup count of log file. default {BACKUP_COUNT}'),
            ]

_EXTRA_KEYS = []


class SimpleLogAdapter(logging.LoggerAdapter):
    """
    >>> LOG = SimpleLogAdapter(logging.getLogger(__name__), ['foo', 'bar'])
    >>> LOG.info('hello, world')
    ... ...
    >>> LOG.info('hello, world', foo='xxx')
    ... ...
    >>> LOG.info('hello, world', foo='xxx', bar='yyy)
    ... ...
    """

    def __init__(self, logger, extra_keys=None):
        """
        Initialize the adapter with a logger and a list object which provides
        contextual key.
        e.g.
            adapter = SimpleLogAdapter(someLogger, ['p1', 'p2'])
        """
        self.extra_keys = extra_keys or {}
        super(SimpleLogAdapter, self).__init__(logger, extra={})

    def process(self, msg, kwargs):
        """
        Process the logging message and keyword arguments passed in.
        All kwargs will be passed to a string like: '[key1: value1]'.
        """
        extras = ', '.join([
            '{}: {}'.format(k, kwargs.pop(k)) for k in self.extra_keys
            if k in kwargs
        ])
        kwargs['extra'] = {'extras': extras and ' [{}]'.format(extras) or ''}
        return msg, kwargs


def basic_config(level=logging.INFO, logfmt=FORMAT, datefmt=DATE_FMT,
                 filename=None, max_mb=None, backup_count=None,
                 extra_keys=None):
    """Init basic logger config.
    If extra_keys is setted, SimpleLogAdapter will be use as logger, you can
    call info like: logger.info('xxx', extra_key1='foo', extra_key2='bar')
    """
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
    if extra_keys:
        global _EXTRA_KEYS

        _EXTRA_KEYS = extra_keys


def load_config(config_file):
    config.fileConfig(config_file)


def getLogger(name):
    """
    >>> basic_config(level=logging.DEBUG)
    >>> LOG = getLogger(__name__)
    >>> LOG.debug('debug')
    >>> LOG.error('error')
    """
    global _EXTRA_KEYS

    if _EXTRA_KEYS:
        return SimpleLogAdapter(logging.getLogger(name),
                                extra_keys=_EXTRA_KEYS)
    else:
        return logging.getLogger(name)


def get_args():
    return [ArgGroup('log arguments', LOG_ARGS)]


def register_arguments(parser):
    for argument in get_args():
        if isinstance(argument, Arg):
            parser.add_argument(*argument.args, **argument.kwargs)
        elif isinstance(argument, ArgGroup):
            log_group = parser.add_argument_group(title='log arguments')
            log_group.add_argument(*argument.args, **argument.kwargs)
        else:
            raise ValueError('Invalid arg class %s', argument.__class__)
