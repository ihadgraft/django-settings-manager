import importlib


class ConfigError(Exception):
    pass


class ConfigItemBase(object):
    default_processors = None  # type: list
    conf = None  # type: list or dict or str

    def __init__(self, conf):
        self.conf = conf
        self.default_processors = [
            'settings_manager.processing.VariableSubstitutionProcessor',
        ]

    def _get_raw_value(self, context):
        raise NotImplementedError

    def _get_processors(self):
        return {
            *self.default_processors,
            *(self.conf.get('_processors', []) if isinstance(self.conf, dict) else [])
        }

    def get_value(self, context):
        result = self._get_raw_value(context)
        for processor in self._get_processors():
            p = processor.split('.')
            module, attr = '.'.join(p[:-1]), p[-1]
            try:
                m = importlib.import_module(module)
            except ImportError as exc:
                raise ConfigError("Processor '%(name)s' could not be loaded" % {"name": processor}) from exc
            result = getattr(m, attr)().process_value(result, context)
        return result


class DefaultConfigItem(ConfigItemBase):

    def _get_raw_value(self, context):
        return self.conf


class ValueLookupConfigItem(ConfigItemBase):

    def _get_raw_value(self, context):
        context_key = self.conf.get('context_key', None)

        key = self.conf.get("key")
        if key is None:
            raise ConfigError("Configuration must provide a value for 'key'")

        if context_key is None:
            source = context
            if key not in context:
                raise ConfigError("Configuration item's 'key' value doesn't exist in the root context. Perhaps a "
                                  "'context_key' is required.")
        else:
            source = context.get(context_key)
            if source is None:
                raise ConfigError(
                    "Context lookup failed with context_key '%(context_key)s'. Available contexts are: %(available)s" % {
                        "context_key": context_key,
                        "available": [k for k, v in context.items() if isinstance(v, dict)]
                    }
                )

        if self.conf['key'] in source:
            return source[self.conf['key']]
        else:
            if 'default' in self.conf:
                return self.conf['default']

            raise ConfigError("Key '%(key)s' does not exist in configuration, and no default is provided" % {
                "key": self.conf["key"]
            })


