import os
import re

import yaml

from settings_manager.handler import EnvironmentVariableHandler


class ConfigurationError(Exception):
    pass


class ConfigLoader(object):
    handlers = None  # type: dict
    variables = None  # type: dict
    default_handlers = None  # type: list
    module = None

    def __init__(self, module):
        self.module = module
        self.handlers = {
            'get_env': EnvironmentVariableHandler(),
        }
        self.default_handlers = []
        self.variables = {}

    def _substitute_variables(self, config, variables):
        if isinstance(config, dict):
            return {k: self._substitute_variables(v, variables) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_variables(v, variables) for v in config]
        elif isinstance(config, str):
            m = re.match(r"^{(?P<name>[^}]+)}$", config)
            if m is not None:
                return variables[m.group("name")]
            return config % variables
        else:
            return config

    def _get_handlers(self, config):
        if not isinstance(config, dict):
            return

        handlers = config.get('_handlers', [{'name': h} for h in self.default_handlers])
        if not isinstance(handlers, list):
            raise ConfigurationError("The value for '_handlers' must be a list")

        for i, h in enumerate(handlers):
            # Check for unsupported settings
            if [k for k in h if k not in ('name', 'kwargs')]:
                raise ConfigurationError("Valid configuration values for a handler are name, kwargs.")

            # Ensure that handler has a name value.
            if 'name' not in h:
                raise ConfigurationError("A name is required for handler %d" % i)

            handler = self.handlers.get(h['name'])
            # Ensure the handler is registered.
            if handler is None:
                raise ConfigurationError("Handler %s is not a registered handler" % h['name'])

            kwargs = h.get('kwargs', {})

            # If kwargs exist, ensure that they are provided as a dict.
            if not isinstance(kwargs, dict):
                raise ConfigurationError("Arguments must be a dict for handler %d" % i)

            yield handler, kwargs

    def _get_value(self, name, config, context):
        for handler, kwargs in self._get_handlers(config):
            config = handler.get_value(context, **kwargs)

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
                        data[scope][k] = self._substitute_variables(data[scope][k], context['variables'])
                        context[scope][k] = self._get_value(k, data[scope][k], context)
                    except Exception as exc:
                        raise ConfigurationError("Error in configuration file '%s', %s.%s" % (file, scope, k)) from exc

        for k in context['settings']:
            setattr(self.module, k, context['settings'][k])

        return context['settings']
