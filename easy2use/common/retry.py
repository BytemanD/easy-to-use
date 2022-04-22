import logging
import time

from easy2use.common import exceptions

LOG = logging.getLogger(__name__)


def retry_for(func, args=(), kwargs=None, interval=1, timeout=None,
              finish_func=None, retry_exceptions=None):
    kwargs = kwargs or {}
    end_time = time.time() + timeout if timeout else None
    retry_times = 0
    while True:
        try:
            result = func(*args, **kwargs)
            if finish_func and finish_func(result):
                break
        except Exception as e:
            if not retry_exceptions or not isinstance(e, *retry_exceptions):
                raise
        if end_time and time.time() >= end_time:
            raise exceptions.LoopTimeout(timeout=timeout, times=retry_times)
        time.sleep(interval)
        retry_times += 1
        LOG.debug('retry function: %s, times=%s', func, retry_times)


def retry_untile_true(func, args=(), kwargs=None, interval=1, timeout=None):
    kwargs = kwargs or {}
    end_time = time.time() + timeout if timeout else None
    retry_times = 0
    while True:
        result = func(*args, **kwargs)
        if result is True:
            break
        if end_time and time.time() >= end_time:
            raise exceptions.RetryTimeout(timeout=timeout, times=retry_times)
        time.sleep(interval)
        retry_times += 1
        LOG.debug('retry function: %s, times=%s', func, retry_times)
