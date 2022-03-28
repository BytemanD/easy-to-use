import time

from easy2use.common import exceptions


class Waiter(object):

    def __init__(self, result, finish):
        self.result = result
        self.finish = finish


def loop_waiter(func, args=(), kwargs={}, interval=1, timeout=None,
                timeout_exc=None):
    end_time = time.time() + timeout if timeout else None
    waiter = Waiter(None, False)
    while True:
        waiter.result = func(*args, **kwargs)
        yield waiter
        if waiter.finish:
            break
        if end_time and time.time() >= end_time:
            raise timeout_exc or exceptions.LoopTimeout(timeout=timeout)
        time.sleep(interval)
