"""
Progress bar
"""
from __future__ import print_function
import contextlib
import logging
import threading
import time
import abc

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from easy2use import date

LOG = logging.getLogger(__name__)


class ProgressBar(abc.ABC):

    def __init__(self, total, description=None):
        self.total = total
        self.description = description or ''

    @abc.abstractmethod
    def update(self, size):
        pass

    def close(self):
        pass

    def set_description(self, *args, **kargs):
        pass


class NopProgressBar(ProgressBar):

    def update(self, size):
        pass


class LoggingBar(ProgressBar):
    padding = '■'
    progress_format = '{} {:>6}% {}'

    def __init__(self, total, description=None, **kwargs):
        super().__init__(total, description)
        self.interval = kwargs.pop('interval', None)
        self.last_time = time.time()
        self.lock = threading.Lock()
        self._progress = 0

    def update(self, size):
        self._progress += size
        if not self.interval or time.time() - self.last_time >= self.interval:
            self.show_progress()
            self.last_time = time.time()

    @property
    def percent(self):
        return self._progress * 100 / self.total

    def set_description(self, description, *args, **kargs):
        self.description = description

    def show_progress(self):
        percent = self.percent
        LOG.info(self.progress_format.format(self.description,
                                             '{:.2f}'.format(percent),
                                             self.padding * int(percent)))


class PrinterBar(LoggingBar):
    padding = '■'
    progress_format = '{} {} {:>6}% [{:100}]\r'

    def show_progress(self):
        self.lock.acquire()
        percent = self._progress * 100 / self.total
        print(self.progress_format.format(date.now_str(), self.description,
                                          '{:.2f}'.format(percent),
                                          self.padding * int(percent)),
              end='')
        self.lock.release()

    def close(self):
        print()


class TqdmBar(PrinterBar):

    def __init__(self, total, *args, description=None, **kwargs):
        super().__init__(total, description)
        kwargs.pop('interval', None)
        self.pbar = tqdm(*args, total=self.total, **kwargs)
        if self.description:
            self.set_description(self.description)

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
