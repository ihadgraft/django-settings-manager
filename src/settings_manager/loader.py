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

    def get_path(self):
        return os.environ.get('DJANGO_ENV_SETTINGS',
                              '/etc/django-settings.yaml')

    def load(self):
        context = {
            'secret': {},
            'env': os.environ,
            'settings': {},
        }

        path = self.get_path()
        try:
            with open(path) as stream:
                context['settings'].update(yaml.safe_load(stream))
        except FileNotFoundError as exc:
            raise SettingsError(
                "File '%(file)s' referenced by DJANGO_ENV_SETTINGS does not "
                "exist" % {"file": path}
            ) from exc

        if self.secret_loader is not None:
            context['secret'].update(
                self.secret_loader.resolve(context['settings'])
            )

        return replace_context(context['settings'], context)
