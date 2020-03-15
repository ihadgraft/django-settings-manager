import os
import yaml
from deepmerge import always_merger
from types import ModuleType
from typing import Any


class SettingsError(Exception):
    pass


class InvalidPathError(SettingsError):
    pass


class SettingsWrapper(object):
    module = None  # type: ModuleType

    def __init__(self, module):
        self.module = module

    def get_value_at_path(self, path):
        """
        Get a value at the given path.

        Args:
            path (str): The path to the object, represented as parent.child.

        Returns:
            Any: The value of the item.

        Raises:
            InvalidPathError: If the path can't be resolved.
        """
        p = path.split('.')  # type: list
        try:
            value = getattr(self.module, p[0])
        except AttributeError:
            raise InvalidPathError("Attribute '%s' is not defined on module" % p[0])

        for i in range(1, len(p)):
            if not isinstance(value, dict):
                raise InvalidPathError("Value at path '%s' is not a dict" % ".".join(p[:i]))
            try:
                value = value[p[i]]
            except KeyError:
                raise InvalidPathError("No key exists at %s" % ".".join(p[:i]))
        return value

    def set_value_at_path(self, path, value):
        """
        Set a value at the given path.

        Args:
            path (str): The path to the object, represented as parent.child.
            value (Any): The value to set at path.

        Returns:
            None:

        Raises:
            InvalidPathError: If the path can't be resolved.
        """
        p = path.split('.')  # type: list

        if len(p) == 1:
            setattr(self.module, p[0], value)
        else:
            if not hasattr(self.module, p[0]):
                setattr(self.module, p[0], {})
            parent = getattr(self.module, p[0])
            i = 0
            for i, key in enumerate(p[1:-1]):
                parent.setdefault(key, {})
                parent = parent[key]
            parent[p[-1]] = value


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
    _config = None  # type: dict
    functions = None  # type: dict

    def __init__(self, path):
        self.functions = {
            "get_env": _get_env,
            "bool": bool,
            "int": int,
        }
        with open(path) as stream:
            self._config = yaml.load(stream, Loader=yaml.FullLoader)

    def configure(self, module):
        for k, v in self._config.get('configure', {}).items():
            setattr(module, k, v)

    def _call_function(self, function_config, substitutions=None):
        if substitutions is None:
            substitutions = {}

        name = function_config['function']
        args = function_config.get('args', [])
        kwargs = function_config.get('kwargs', {})

        for i in range(len(args)):
            if args[i] in substitutions:
                args[i] = substitutions[args[i]]

        for k in kwargs.items():
            kwargs[k] = substitutions.get(kwargs[k], kwargs[k])

        return self.functions[name](*args, **kwargs)

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

            value = self._call_function(inject)
            for processor in inject.get('value_processors', []):
                value = self._call_function(processor, {':value:': value})
            _set_for_key(item, keys[-1], value)


