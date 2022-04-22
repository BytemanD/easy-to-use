import abc
import contextlib
import itertools
import threading
import time

DEFAULT_SPEED = 10


class BaseSpinner(object):

    def __init__(self, speed=None, description=None):
        self.speed = speed or DEFAULT_SPEED
        self.description = description
        self.thread = None
        self._close = threading.Event()

    def close(self):
        self._stop = True
        self._close.set()
        self.thread.join()
        print(' ' * 100, end='\r')

    def start(self):
        self.thread = threading.Thread(target=self._start)
        self.thread.setDaemon(True)
        self.thread.start()

    def _start(self):
        interval = 1 / self.speed
        while not self._close.is_set():
            print('{} {}'.format(self.draw(), self.description or ''),
                  end='\r')
            time.sleep(interval)
        return self

    def set_description(self, desription):
        self.description = desription

    @abc.abstractmethod
    def draw(self):
        pass


class RotatingLine(BaseSpinner):
    cycle = itertools.cycle(['|', '/', '—', '\\'])

    def draw(self):
        return next(self.cycle)


class Point(BaseSpinner):
    count = itertools.cycle(range(20))

    def draw(self):
        left = next(self.count)
        return '[{}·●·{}]'.format(' ' * left, ' ' * (20 - left))


@contextlib.contextmanager
def spinner(driver='point', **kwargs):
    """
    e.g.
    >>> with spinner() as bar:
    >>>     # do something
    >>>     bar.set_description('foo')
    """
    if driver == 'rotating_line':
        bar = RotatingLine(**kwargs)
    elif driver == 'point':
        bar = Point(**kwargs)
    bar.start()
    yield bar
    bar.close()
