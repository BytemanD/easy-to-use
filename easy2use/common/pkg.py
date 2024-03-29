import importlib
from importlib import metadata


def import_class(class_path):
    mod, _, klass = class_path.rpartition('.')
    return getattr(importlib.import_module(mod), klass)


def package_version(name):
    try:
        dist = metadata.distribution(name)
        version = dist.version
    except metadata.PackageNotFoundError:
        version = None

    return version


class PackageVersion(object):

    def __init__(self, version):
        self.version = isinstance(version, list) and version or \
            version.split('.')
        if self.version[0].lower().startswith('v'):
            self.version[0] = self.version[0][1:]
        self.is_dev = 'dev' in self.version[-1]

    @property
    def version_list(self):
        return self.version[:-1] if self.is_dev else self.version

    def __lt__(self, other):
        return self._compare(other) < 0

    def __eq__(self, other):
        return self._compare(other) == 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def _compare(self, other):
        for v1, v2 in zip(self.version_list, other.version_list):
            if int(v1) > int(v2):
                return 1
            if int(v1) < int(v2):
                return -1

        if self.is_dev and not other.is_dev:
            return -1
        elif not self.is_dev and other.is_dev:
            return 1
        elif not self.is_dev:
            return 0

        dev1_num = int(self.version[-1].replace('dev', ''))
        dev2_num = int(other.version[-1].replace('dev', ''))
        return dev1_num - dev2_num
