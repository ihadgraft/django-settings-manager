import os
import re


class AbstractConfigHandler(object):
    def get_value(self, name, config, context, **kwargs):
        raise NotImplementedError


class VariableSubstitutionHandler(AbstractConfigHandler):

    def get_value(self, name, config, context, **kwargs):

        if isinstance(config, dict):
            return {k: self.get_value(name, v, context) for k, v in config.items()}
        elif isinstance(config, list):
            return [self.get_value(name, v, context) for v in config]
        elif isinstance(config, str):
            m = re.match(r"^{(?P<name>[^}]+)}$", config)
            if m is not None:
                return context['variables'][m.group("name")]
            return config % context['variables']
        else:
            return config


class EnvironmentVariableHandler(AbstractConfigHandler):

    def get_value(self, name, config, context, **kwargs):
        key = kwargs['key']
        if key in os.environ:
            return os.environ[key]

        if 'default' in kwargs:
            return kwargs['default']

        raise KeyError("Key '%s' is not defined in environment, and no default is provided")
