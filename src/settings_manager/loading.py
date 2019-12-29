import re
import os
from typing import Any

import yaml

from settings_manager.utils import load_module_attr


class ConfigurationItemError(Exception):
    pass


class InvalidConfigurationItemType(ConfigurationItemError):
    pass


class ConfigurationItem(object):
    ALLOWED_TYPES = ('setting', 'variable')

    name = None  # type: str
    _conf = None  # type: dict
    _value = None  # type: Any
    context = None  # type: dict

    def __init__(self, name, conf):
        self.name = name
        self._conf = conf

        # validate type
        if self.type not in self.ALLOWED_TYPES:
            raise InvalidConfigurationItemType("Value %s is not one of the allowed configuration item types: %s", (
                self.type, ", ".join(self.ALLOWED_TYPES)
            ))

    @property
    def type(self):
        if isinstance(self._conf, str):
            return 'setting'
        return self._conf.get('_meta', {}).get('type', 'setting')

    @property
    def value(self):
        if isinstance(self._conf, str):
            return self._conf
        if '_value' in self._conf:
            value = self._conf['_value']
        else:
            value = {k: v for k, v in self._conf.items() if k != '_meta'}

        for p_meta in self._conf.get('_meta', {}).get('processors', []):
            p = load_module_attr(p_meta['name'])
            value = p(value, **p_meta.get('kwargs', {}))

        return value


def load_settings_files(settings_dirs):
    result = []
    for d in settings_dirs:
        for f in [os.path.join(d, n) for n in os.listdir(d) if re.search(r"\.ya?ml$", n) is not None]:
            with open(f) as stream:
                data = yaml.load(stream, Loader=yaml.FullLoader)
            data.setdefault('_meta', {})
            data['_meta']['file'] = f
            result.append(data)

    return sorted(result, key=lambda e: e.get('_meta', {}).get('priority', 0))


def apply_context(value, context):
    if isinstance(value, dict):
        return {k: apply_context(v, context) for k, v in value.items()}
    elif isinstance(value, list):
        return [apply_context(v, context) for v in value]
    elif isinstance(value, str):
        return value % context
    else:
        return value


def parse_settings_data(data, context=None):
    settings = {}
    if context is None:
        context = {}

    for k in [k for k in data if not k.startswith('_')]:
        item = ConfigurationItem(k, data[k])
        value = apply_context(item.value, context)
        if item.type == 'variable':
            context[item.name] = value
        elif item.type == 'setting':
            settings[item.name] = value
    return settings
