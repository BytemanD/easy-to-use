import time


class LocalCache(object):

    def __init__(self, expired=None):
        self.expired = expired
        self._data = {}

    def get(self, key):
        cached = self._data.get(key)
        if cached:
            expired_at = cached.get('expered_at')
            if expired_at and time.time() > expired_at:
                del self._data[key]
                cached = None
        return cached

    def set(self, key, value):
        """
        {'key1': {'expered_at': <time>, 'data': value}:
         'key2': {'expered_at': <time>, 'data': value}}
        """
        cached = {'data': value}
        if self.expired:
            cached['expered_at'] = time.time() + self.expired
        self._data[key] = cached
