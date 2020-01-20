import os
import yaml
import json


class AbstractConfigHandler(object):

    def get_value(self, context, **kwargs):
        raise NotImplementedError


class EnvironmentVariableHandler(AbstractConfigHandler):

    def get_value(self, context, key=None, **kwargs):
        if key in os.environ:
            return os.environ[key]

        if 'default' in kwargs:
            return kwargs['default']

        raise KeyError("Key '%s' is not defined in environment, and no default is provided")


class FileVariableHandler(AbstractConfigHandler):

    def get_value(self, context, file=None, parser='str_trimmed', **kwargs):
        parsers = {
            'str': lambda s: s.read(),
            'str_trimmed': lambda s: s.read().strip(),
            'yaml': lambda s: yaml.safe_load(s),
            'json': lambda s: json.load(s),
            'int': lambda s: int(s.read().strip()),
            'float': lambda s: float(s.read().strip()),
        }
        if parser not in parsers.keys():
            raise ValueError("Format must be one of: %s" % ", ".join(parsers.keys()))

        with open(file) as stream:
            return parsers[parser](stream)
