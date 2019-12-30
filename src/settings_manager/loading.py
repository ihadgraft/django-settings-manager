import copy
import importlib
import os

import yaml

from settings_manager.config_items import DefaultConfigItem, ConfigError
from settings_manager.utils import list_files


def get_config_item(value, meta):
    """
    Get the configuration type of a configuration item.

    Args:
        conf (dict or list or str): The configuration.
    Returns:
        ConfigItemBase: A configuration type.
    """
    if 'type' in meta:
        p = meta['type'].split('.')
        module, attr = '.'.join(p[:-1]), p[-1]
        m = importlib.import_module(module)
        return getattr(m, attr)(value, meta)
    return DefaultConfigItem(value, meta)


def load_config_files(dir_list):
    data = []
    for file_path in list_files(dir_list, r"\.ya?ml$"):
        with open(file_path) as stream:
            d = yaml.load(stream, Loader=yaml.FullLoader)
            d.setdefault('_meta', {})
            d['_meta']['file'] = file_path
            data.append(d)

    result = {}
    context = {
        "env": dict(os.environ)
    }
    for settings in sorted(data, key=lambda e: e['_meta'].get('priority', 0)):
        for k in filter(lambda e: e not in ('_meta',), settings):
            meta = {}
            if isinstance(settings[k], dict):
                if '_value' in settings[k]:
                    conf = settings[k].pop('_value')
                else:
                    conf = {k: v for k, v in settings[k].items() if not k.startswith('_')}
                meta = {k.replace('_', '', 1): v for k, v in settings[k].items() if k.startswith('_')}
            else:
                conf = settings[k]
            print(conf, meta)
            item = get_config_item(conf, meta)
            try:
                result[k] = item.get_value(context)
            except ConfigError as exc:
                raise ConfigError("Error processing item %(key)s in file %(file)s" % {
                    "key": k, "file": settings['_meta']['file'],
                }) from exc

    return result


# class ConfigurationItemError(Exception):
#     pass
#
#
# class InvalidConfigurationItemType(ConfigurationItemError):
#     pass
#
#
# class ConfigurationItem(object):
#     ALLOWED_TYPES = ('setting', 'variable')
#
#     name = None  # type: str
#     meta = None  # type: dict
#     _value = None  # type: Any
#
#     def __init__(self, name, meta, value):
#         self.name = name
#         self.meta = meta
#         self._value = value
#
#         # validate type
#         if self.type not in self.ALLOWED_TYPES:
#             raise InvalidConfigurationItemType("Value %s is not one of the allowed configuration item types: %s", (
#                 self.type, ", ".join(self.ALLOWED_TYPES)
#             ))
#
#     @property
#     def type(self):
#         return self.meta.get('type', 'setting')
#
#     @property
#     def value(self):
#         value = self._value
#
#         for p_meta in self.meta.get('processors', []):
#             p = load_module_attr(p_meta['name'])
#             value = p(value, **p_meta.get('kwargs', {}))
#
#         return value
#
# class ConfigurationParser(object):
#     configuration_dirs = None  # type: dict
#     initial_context = None  # type: dict
#
#     def __init__(self, configuration_dirs, initial_context=None):
#         if initial_context is None:
#             initial_context = {}
#         self.configuration_dirs = configuration_dirs
#         self.initial_context = initial_context
#
#     def _replace_context_vars(self, value, context):
#         if isinstance(value, dict):
#             return {k: self._replace_context_vars(v, context) for k, v in value.items()}
#         elif isinstance(value, list):
#             return [self._replace_context_vars(v, context) for v in value]
#         elif isinstance(value, str):
#             return value % context
#
#     def _run_value_processors(self, value, meta):
#         result = copy.deepcopy(value)
#         for p_meta in meta.get('processors', []):
#             p = load_module_attr(p_meta['name'])
#             result = p(result, **p_meta.get('kwargs', {}))
#         return result
#
#     def _parse_file(self, data, context):
#         settings = {}
#         for k in [k for k in data if not k.startswith('_')]:
#             meta = {}
#             value = data[k]
#             if isinstance(value, dict):
#                 meta = value.pop('_meta', {})
#                 value = value.get('_value', value)
#
#             value = self._replace_context_vars(value, context)
#             value = self._run_value_processors(value, meta)
#
#             value_type = meta.get('type', 'setting')
#             if value_type == 'variable':
#                 context[k] = value
#             elif value_type == 'setting':
#                 settings[k] = value
#             else:
#                 raise ValueError("%(var_name)s._meta.type must be either 'setting' or 'variable' in %(file)s" % {
#                     "var_name": k, "file": data["_meta"]["file"]
#                 })
#
#
#     def parse(self):
#         result = []
#         for d in self.configuration_dirs:
#             for f in [os.path.join(d, n) for n in os.listdir(d) if re.search(r"\.ya?ml$", n) is not None]:
#                 with open(f) as stream:
#                     data = yaml.load(stream, Loader=yaml.FullLoader)
#                 data.setdefault('_meta', {})
#                 data['_meta']['file'] = f
#                 result.append(data)
#
#         context = copy.deepcopy(self.initial_context)
#         for data in sorted(result, key=lambda e: e.get('_meta', {}).get('priority', 0)):
#             self._parse_file(data, context)


