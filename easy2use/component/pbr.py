"""
Progress bar
"""
from __future__ import print_function
import contextlib
import logging
import threading
import time

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from easy2use import date

LOG = logging.getLogger(__name__)


class ProgressBar(object):

    def __init__(self, total, description=None, **kwargs):
        self.total = total
        self.interval = kwargs.get('interval')
        self.description = description

    def update(self, size):
        pass

    def close(self):
        pass

    def set_description(self, *args, **kargs):
        pass


class PrinterBar(object):
    padding = '■'
    progress_format = '{} {} {:>6}% [{:100}]\r'

    def __init__(self, total, description=None, **kwargs):
        self.total = total
        self.interval = kwargs.get('interval')
        self.description = description or ''
        self.last_time = time.time()
        self.lock = threading.Lock()
        self._progress = 0

    def update(self, size):
        self._progress += size
        if not self.interval or time.time() - self.last_time >= self.interval:
            self.show_progress()
            self.last_time = time.time()

    def set_description(self, description, *args, **kargs):
        self.description = description

    def show_progress(self):
        self.lock.acquire()
        percent = self._progress * 100 / self.total
        print(self.progress_format.format(date.now_str(), self.description,
                                          '{:.2f}'.format(percent),
                                          self.padding * int(percent)),
              end='')
        self.lock.release()

    @property
    def percent(self):
        return self._progress * 100 / self.total

    def close(self):
        print()


class LoggingBar(PrinterBar):
    progress_format = '{} {:>6}% {}'

    def show_progress(self):
        percent = self.percent
        LOG.info(self.progress_format.format(self.description,
                                             '{:.2f}'.format(percent),
                                             self.padding * int(percent)))


class TqdmBar(PrinterBar):

    def __init__(self, total, *args, **kwargs):
        kwargs.pop('interval', None)
        description = kwargs.pop('description')
        kwargs['total'] = total
        self.pbar = tqdm(*args, **kwargs)
        if description:
            self.set_description(description)

    def update(self, size):
        self.pbar.update(size)

    def close(self):
        self.pbar.clear()
        self.pbar.close()

    def set_description(self, *args, **kwargs):
        self.pbar.set_description(*args, **kwargs)


def factory(total, description=None, interval=None, driver=None):
    bar_cls = None
    driver = driver or 'tqdm'
    if driver == 'logging':
        bar_cls = LoggingBar
    elif driver == 'tqdm':
        if tqdm:
            bar_cls = TqdmBar
        else:
            LOG.warning('tqdm is not installed, use PrinterBar.')
    bar_cls = bar_cls or PrinterBar
    return bar_cls(total, description=description, interval=interval)


@contextlib.contextmanager
def progressbar(*args, **kwargs):
    """
    e.g.
    >>> with progressbar(10, description='foo') as bar:
    >>>    for _ in range(10):
    >>>        bar.update(1)
    """
    bar = factory(*args, **kwargs)
    yield bar
    bar.close()


# bar = factory(10, description='xxxxx', )
