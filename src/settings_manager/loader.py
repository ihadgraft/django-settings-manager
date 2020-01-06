import copy
import os
import re
import yaml

from settings_manager.exceptions import ConfigurationError
from settings_manager.handler import VariableSubstitutionHandler, EnvironmentVariableHandler


class ConfigLoader(object):
    handlers = None
    variables = None

    def __init__(self):
        self.handlers = {
            'substitute_variables': VariableSubstitutionHandler(),
            'get_env': EnvironmentVariableHandler(),
        }
        self.variables = {}

    def _get_value(self, name, config, context):
        if '_handlers' in config:
            if not isinstance(config['_handlers'], list):
                raise ConfigurationError("The _handlers property must be a list in %s" % name)
            handlers = []
            for i, h in enumerate(config['_handlers']):
                if [k for k in h if k not in ('name', 'kwargs')]:
                    raise ConfigurationError("Valid configuration values for a handler are name, kwargs")
                if 'name' not in h:
                    raise ConfigurationError("A name is required for handler %s.%d" % (name, i))
                if h['name'] not in self.handlers:
                    raise ConfigurationError("Handler %s.%s is not a registered handler" % (name, h['name']))
                if 'kwargs' in h and not isinstance(h['kwargs'], dict):
                    raise ConfigurationError("Arguments must be a dict for handler %s.%d" % (name, i))
                handlers.append((self.handlers[h['name']], h.get('kwargs', {})))
        else:
            handlers = [(self.handlers['substitute_variables'], {})]

        for handler, kwargs in handlers:
            config = handler.get_value(name, config, context, **kwargs)

        return config

    def _get_data(self, dir_list):
        data = []
        for d in dir_list:
            for file in [os.path.join(d, f) for f in os.listdir(d) if re.search(r"\.ya?ml$", f) is not None]:
                with open(file) as stream:
                    data.append((file, yaml.load(stream, Loader=yaml.FullLoader)))
        return sorted(data, key=lambda e: e[1].get('_meta', {}).get('priority', 10))

    def load(self, dir_list):
        context = {
            'variables': self.variables.copy(),
            'settings': {},
        }

        for file, data in self._get_data(dir_list):
            for scope in ('variables', 'settings'):
                for k in data.get(scope, {}):
                    try:
                        context[scope][k] = self._get_value(k, data[scope][k], context)
                    except Exception as exc:
                        raise ConfigurationError("Error in configuration file '%s', %s.%s" % (file, scope, k))

        return context['settings']
