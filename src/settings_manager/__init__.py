import os
import yaml
from deepmerge import always_merger
from types import ModuleType


def get_accessor_functions(obj):
    if isinstance(obj, dict):
        def _get(key):
            return obj[key]

        def _set(key, value):
            obj[key] = value
    elif isinstance(obj, ModuleType):
        def _get(key):
            return getattr(obj, key)

        def _set(key, value):
            setattr(obj, key, value)
    else:
        raise TypeError("Wrong type for object at %s" % repr(obj))
    return _get, _set


def get_value_for_path(root, path, index=0):
    p = path.split('.')
    key = p[index]

    _get, _set = get_accessor_functions(root)

    try:
        if key == p[-1]:
            return _get(p[-1])
        next_root = _get(key)
    except (AttributeError, KeyError) as exc:
        raise InvalidPathError(p[:index + 1]) from exc

    return get_value_for_path(next_root, path, index + 1)


def set_value_for_path(root, path, value, index=0):
    p = path.split('.')
    key = p[index]

    _get, _set = get_accessor_functions(root)

    try:
        try:
            if key == p[-1]:
                _set(key, value)
                return
            next_root = _get(key)
        except (AttributeError, KeyError):
            _set(key, {})
            next_root = _get(key)
        set_value_for_path(next_root, path, value, index + 1)
    except TypeError as exc:
        raise InvalidPathError(p[:index + 1], "Not a dict or module at path '%(path)s'") from exc


class SettingsError(Exception):
    pass


class InvalidPathError(SettingsError):

    def __init__(self, path, message="Value not valid at '%(path)s'"):
        super().__init__(message % {"path": ".".join(path)})


def _get_env(key):
    return os.environ[key]


def _str_to_bool(value):
    if value.lower() in ("1", "true", "yes"):
        return True
    elif value.lower() in ("0", "false", "no"):
        return False
    else:
        raise ValueError("Could not translate value '%s' to a bool" % value)


class SettingsManager(object):
    _config = None  # type: dict
    functions = None  # type: dict

    def __init__(self, settings_file_path):
        self.functions = {
            "get_env": _get_env,
            "str_to_bool": _str_to_bool,
            "int": int,
        }
        with open(settings_file_path) as stream:
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
            value = self._call_function(inject)
            for processor in inject.get('value_processors', []):
                value = self._call_function(processor, {'<<value>>': value})
            set_value_for_path(module, k, value)


