import importlib


def load_module_attr(cls_string):
    parts = cls_string.split('.')
    package, module, attr = parts[:-2], parts[-2], parts[-1]
    m = importlib.import_module(module, package)
    return getattr(m, attr)
