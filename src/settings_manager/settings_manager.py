import os
import yaml
from deepmerge import always_merger
from types import ModuleType


class SettingsError(Exception):
    pass


class InvalidPathError(SettingsError):

    def __init__(self, path, message="Value not valid at '%(path)s'"):
        super().__init__(message % {"path": ".".join(path)})


class PathSearch(object):
    module = None  # type: ModuleType

    def __init__(self, module):
        self.module = module

    def _get_root(self, path):
        try:
            return getattr(self.module, path[0])
        except AttributeError as exc:
            raise InvalidPathError(path[0]) from exc

    @staticmethod
    def non_dict_error(path):
        return InvalidPathError(path, message="Can't traverse through a non-dict at '%(path)s'")

    def get(self, path):
        path = path.split('.')
        item = self._get_root(path)
        for i, k in enumerate(path[1:]):
            if not isinstance(item, dict):
                raise self.non_dict_error(path[:i+1])
            try:
                item = item[k]
            except KeyError as exc:
                raise InvalidPathError(path[:i+1]) from exc
        return item

    def set(self, path, value):
        path = path.split('.')

        if len(path) == 1:
            setattr(self.module, path[0], value)
            return

        item = self._get_root(path)
        for i, k in enumerate(path[1:-1]):
            if not isinstance(item, dict):
                raise self.non_dict_error(path[:i+1])
            try:
                item = item[k]
            except KeyError as exc:
                raise InvalidPathError(path[:i+1]) from exc

        if not isinstance(item, dict):
            raise self.non_dict_error(path[:-1])

        item[path[-1]] = value


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


