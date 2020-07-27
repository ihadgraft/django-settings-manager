import os
import yaml
from typing import Any
from .secret import AbstractSecretLoader
import jinja2


class SettingsError(Exception):
    pass


def replace_context(value: Any, context: dict):
    """
    Traverse a dict object and, upon finding a string with template delimiters,
    process the string as a template with given context.

    @param value: The value to process.
    @param context: The context to use if value is a template string.

    @return The result of the replacement. For non-recursive calls, this is a
    dict.
    """
    if isinstance(value, dict):
        return {k: replace_context(value[k], context) for k in value}
    elif isinstance(value, list):
        return [replace_context(v, context) for v in value]
    elif isinstance(value, str) and (('{{' in value) or ('{%' in value)):
        tpl = jinja2.Template(value)
        return tpl.render(context)
    else:
        return value


class SettingsLoader(object):
    secret_loader = None  # type: AbstractSecretLoader

    def __init__(self, secret_loader: AbstractSecretLoader = None):
        self.secret_loader = secret_loader

    def _load_settings(self):
        path = os.environ.get('DJANGO_ENV_SETTINGS',
                              '/etc/django-settings.yaml')
        try:
            with open(path) as stream:
                return yaml.safe_load(stream)
        except FileNotFoundError as exc:
            raise SettingsError(
                "File '%(file)s' referenced by DJANGO_ENV_SETTINGS does not "
                "exist" % {"file": path}
            ) from exc

    def _get_context(self) -> dict:
        return {
            'secret': {},
            'env': os.environ,
            'settings': {},
        }

    def _after_settings_loaded(self, settings: dict) -> dict:
        """
        Subclasses can override this to modify settings after they are loaded,
        but before they are processed.
        """
        return settings

    def _after_settings_processed(self, settings: dict) -> dict:
        """
        Subclasses can override this to modify settings after secrets are
        resolved and templates are processed.
        """
        return settings

    def load(self):
        context = self._get_context()
        loaded_settings = self._load_settings()
        loaded_settings = self._after_settings_loaded(loaded_settings)
        if self.secret_loader is not None:
            context['secret'].update(
                self.secret_loader.resolve(loaded_settings)
            )
        context['settings'] = loaded_settings
        result = replace_context(loaded_settings, context)
        return self._after_settings_processed(result)
