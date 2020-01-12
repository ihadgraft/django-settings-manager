import os


class AbstractConfigHandler(object):
    def get_value(self, context, **kwargs):
        raise NotImplementedError


class EnvironmentVariableHandler(AbstractConfigHandler):

    def get_value(self, context, **kwargs):
        key = kwargs['key']
        if key in os.environ:
            return os.environ[key]

        if 'default' in kwargs:
            return kwargs['default']

        raise KeyError("Key '%s' is not defined in environment, and no default is provided")


