import importlib
import pkg_resources


def import_class(class_path):
    mod, _, klass = class_path.rpartition('.')
    return getattr(importlib.import_module(mod), klass)


def package_version(name):
    try:
        version = pkg_resources.get_distribution(name).version
    except pkg_resources.DistributionNotFound:
        version = None

    return version
