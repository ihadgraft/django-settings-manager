import importlib


class ConfigError(Exception):
    pass


class ConfigTypeBase(object):
    conf = None  # type: list or dict or str

    def __init__(self, conf):
        self.conf = conf

    def _get_raw_value(self, context):
        raise NotImplementedError

    def _substitute_variables(self, value, context):
        if isinstance(value, dict):
            return {k: self._substitute_variables(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_variables(v, context) for v in value]
        elif isinstance(value, str):
            return value % context
        return value

    def get_value(self, context):
        result = self._get_raw_value(context)
        result = self._substitute_variables(result, context)
        return result


class DefaultConfigType(ConfigTypeBase):

    def _get_raw_value(self, context):
        return self.conf


class ValueLookupConfigType(ConfigTypeBase):

    def _get_raw_value(self, context):
        source_key = self.conf.get('source', 'env')

        if 'key' not in self.conf:
            raise ConfigError("Configuration data must provide a value for 'key'")

        if source_key not in context:
            raise ConfigError("Configuration item's 'source' value doesn't exist in context.")

        source = context[source_key]
        if self.conf['key'] in source:
            return source[self.conf['key']]
        else:
            if 'default' in self.conf:
                return self.conf['default']

            raise ConfigError("Key '%(key)s' does not exist in configuration, and no default is provided" % {
                "key": self.conf["key"]
            })


def get_config_item(conf):
    """
    Get the configuration type of a configuration item.

    Args:
        conf (dict or list or str): The configuration.
    Returns:
        ConfigTypeBase: A configuration type.
    """
    if isinstance(conf, dict) and '_type' in conf:
        p = conf['_type'].split('.')
        module, attr = '.'.join(p[:-1]), p[-1]
        m = importlib.import_module(module)
        return getattr(m, attr)(conf)
    return DefaultConfigType(conf)
