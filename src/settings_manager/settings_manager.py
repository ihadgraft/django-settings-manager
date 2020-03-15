import os
import yaml
from deepmerge import always_merger
from types import ModuleType
from typing import Any


class SettingsError(Exception):
    pass


def _get_for_key(obj, key):
    """
    Get a dict value or object attribute.

    Arguments:
        obj (dict or ModuleType): The object to get the value from.
        key (str): The key to retrieve.
    Returns:
        Any: The value obtained at the key.
    Raises:
        KeyError: If obj is a dict and the key is not found.
        AttributeError: If obj is a module and the key is not found.
    """
    if isinstance(obj, dict):
        return obj[key]
    else:
        return getattr(obj, key)


def _set_for_key(obj, key, value):
    """
    Set a dict value or object attribute.

    Arguments:
        obj (dict or ModuleType): The object to get the value from.
        key (str): The key to retrieve.
        value (Any):
    Returns:
        Any: The value obtained at the key.
    """
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)
    return value


def _get_env(key):
    return os.environ[key]


class SettingsManager(object):
    TRUE_STRINGS = ('true', 'yes', '1')
    _config = None  # type: dict
    functions = None  # type: dict

    def __init__(self, path):
        self.functions = {
            "get_env": _get_env,
        }
        with open(path) as stream:
            self._config = yaml.load(stream, Loader=yaml.FullLoader)

    def configure(self, module):
        for k, v in self._config.get('configure', {}).items():
            setattr(module, k, v)

    def override(self, module):
        for k, v in self._config.get('override', {}).items():
            if hasattr(module, k):
                current = getattr(module, k)
                if isinstance(current, dict):
                    v = always_merger.merge(current, v)
            setattr(module, k, v)

        for k, inject in self._config.get('inject', {}).items():
            keys = k.split('.')
            item = module
            for index, key in enumerate(keys[:-1]):
                try:
                    item = _get_for_key(item, key)
                except (KeyError, AttributeError):
                    item = _set_for_key(item, key, {})

            f, args, kwargs = (
                inject[0],
                inject[1] if len(inject) > 1 else [],
                inject[2] if len(inject) > 2 else {}
            )
            _set_for_key(item, keys[-1], self.functions[f](*args, **kwargs))


