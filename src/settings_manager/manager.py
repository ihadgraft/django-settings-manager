from typing import Callable, Dict
from settings_manager.handler import HandlerValueNotProvided
from settings_manager.utils import load_files, substitute_variables
from collections import OrderedDict


class OmitFromConfig(Exception):
    pass


class ConfigurationItem(object):
    name = None  # type: str
    handler = None  # type: Callable
    default = None  # type: str
    required = None  # type: bool
    help_text = None  # type: str

    def __init__(self, name, handler, required=False, default=None, help_text=''):
        self.name = name
        self.handler = handler
        self.required = required
        self.default = default
        self.help_text = help_text

    def get_value(self, **kwargs):
        try:
            return self.handler(**kwargs)
        except HandlerValueNotProvided as exc:
            if self.required:
                raise HandlerValueNotProvided("Missing required value for %s" % self.name)
            return self.default


class Setting(ConfigurationItem):
    pass


class Variable(ConfigurationItem):
    pass


class ConfigManager(object):
    configuration_items = None  # type: Dict[str, ConfigurationItem]

    def __init__(self):
        self.configuration_items = dict()

    def register(self, configuration_item):
        self.configuration_items[configuration_item.name] = configuration_item

    def get_info(self):
        result = OrderedDict((('variables', OrderedDict()), ('settings', OrderedDict())))

        def _add(scope, name, item):
            result[scope][name] = {
                "name": name,
                "help_text": item.help_text,
                "handler": {
                    "name": "%s.%s" % (item.handler.__module__, item.handler.__name__),
                }
            }
            if item.handler.kwargs:
                result[scope][name]["handler"]["arguments"] = OrderedDict()
                for argument in item.handler.kwargs:
                    result[scope][name]["handler"]["arguments"][argument.name] = {
                        "name": argument.name,
                        "required": argument.required,
                        "help_text": argument.help_text,
                    }

        for name, item in [(n, i) for n, i in self.configuration_items.items() if isinstance(i, Variable)]:
            _add("variables", name, item)

        for name, item in [(n, i) for n, i in self.configuration_items.items() if isinstance(i, Setting)]:
            _add("settings", name, item)

        return result

    def load(self, dir_list, module):
        variables = dict()
        for file, data in load_files(dir_list):
            for name, conf in {k: v for k, v in data.items() if k not in ('_meta',)}.items():
                item = self.configuration_items.get(name)
                if item:
                    scope = 'variable' if isinstance(item, Variable) else 'setting'
                    value = item.handler(**substitute_variables(conf, variables))
                else:
                    value = substitute_variables(item, variables)
                    scope = 'setting'

                if scope == 'variable':
                    variables[name] = value

                print(name, scope, value)
