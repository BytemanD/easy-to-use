import importlib


def import_class(class_path):
    mod, _, klass = class_path.rpartition('.')
    return getattr(importlib.import_module(mod), klass)
