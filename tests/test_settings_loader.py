from settings_manager.loader import SettingsLoader, replace_context
from settings_manager.secret import AbstractSecretLoader
import os


def test_replace_context():
    conf = {
        'NAME': 'John',
        'items': [
            '{{ settings.NAME }}',
        ]
    }
    v = replace_context(conf, {'settings': conf})
    assert v == {
        'NAME': 'John',
        'items': ['John'],
    }


def test_load(create_settings_file, monkeypatch):
    class _SecretLoader(AbstractSecretLoader):
        def resolve(self, settings: dict) -> dict:
            return {'SHH': 'secret_value'}

    f = create_settings_file({
        'NAME': 'John',
        'FILE': '{{ env.DJANGO_ENV_SETTINGS }}',
        'SECRET': '{{ secret.SHH }}'
    })
    monkeypatch.setitem(os.environ, 'DJANGO_ENV_SETTINGS', f)
    loader = SettingsLoader(_SecretLoader())
    settings = loader.load()
    assert settings == {
        'NAME': 'John',
        'FILE': f,
        'SECRET': 'secret_value',
    }
