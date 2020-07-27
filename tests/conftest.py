import pytest
import os
import yaml
from hvac.exceptions import VaultError


@pytest.fixture()
def hvac_client():

    class _Client(object):
        url = None  # type: str
        auth = None  # type: tuple
        secret_map = None  # type: dict

        def __init__(self, url: str, **kwargs):
            self.url = url
            self.secret_map = {}

            def _read_secret(path: str, mount_point: str = 'secret'):
                try:
                    return self.secret_map[1][mount_point][path]
                except AttributeError:
                    raise VaultError("No such item")

            def _read_secret_version(path: str, version: int = 1, mount_point:
                                     str = 'secret'):
                try:
                    return self.secret_map[2][mount_point][path][version]
                except AttributeError:
                    raise VaultError("No such item")

            self.secrets = type('test', (object,), {})
            self.secrets.kv = type('test', (object,), {})
            self.secrets.kv.v1 = type('test', (object,), {})
            self.secrets.kv.v2 = type('test', (object,), {})
            self.secrets.kv.v1.read_secret = _read_secret
            self.secrets.kv.v2.read_secret_version = _read_secret_version

        def auth_approle(self, role_id, secret_id, **kwargs):
            self.auth = (role_id, secret_id)

    return _Client


@pytest.fixture()
def create_settings_file(tmp_path):
    def _save(settings: dict):
        f = os.path.join(tmp_path, 'settings.yaml')
        with open(f, 'wt') as stream:
            yaml.dump(settings, stream)
        return f
    return _save
