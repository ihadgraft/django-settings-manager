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

    def __init__(self, name, conf):
        self.name = name
        self._conf = conf

        # validate type
        if self.type not in self.ALLOWED_TYPES:
            raise InvalidConfigurationItemType("Value %s is not one of the allowed configuration item types: %s", (
                self.type, ", ".join(self.ALLOWED_TYPES)
            ))

        # validate priority
        if not isinstance(self.priority, int):
            raise ConfigurationItemError("Priority must be an int")

    @property
    def type(self):
        return self._conf.get('_meta', {}).get('type', 'setting')

    @property
    def priority(self):
        return self._conf.get('_meta', {}).get('priority', 0)

    @property
    def value(self):
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
