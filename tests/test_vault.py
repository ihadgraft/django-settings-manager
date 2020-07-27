import hvac
import os
from settings_manager.vault import (
    AbstractVaultSecretLoader, AbstractVaultReader, VaultAppRoleSecretLoader
)


def test_resolve(hvac_client, monkeypatch):
    class _Reader(AbstractVaultReader):
        def read(self, client: hvac.Client, path: str, **kwargs):
            if path == 'foo/bar':
                return 'bar_secret'
            elif path == 'foo/baz':
                return 'baz_secret'

    class _Loader(AbstractVaultSecretLoader):
        def _init_client(self, settings: dict):
            self.client = hvac_client('https://127.0.0.1:8200')

    c = _Loader(_Reader())
    settings = {
        'VAULT_SECRETS': {
            'bar': 'foo/bar',
            'baz': 'foo/baz',
        }
    }
    assert c.resolve(settings) == {
        'bar': 'bar_secret',
        'baz': 'baz_secret'
    }


def test_approle_secret_loader(hvac_client, monkeypatch):
    settings = {
        'VAULT_ADDR': 'https://127.0.0.1:8200',
        'VAULT_ROLE_ID': 'abc',
    }
    monkeypatch.setattr(VaultAppRoleSecretLoader, 'client_cls', hvac_client)
    monkeypatch.setitem(os.environ, 'VAULT_SECRET_ID', '123')
    loader = VaultAppRoleSecretLoader(AbstractVaultReader())
    loader.resolve(settings)
    assert loader.client.url == 'https://127.0.0.1:8200'
    assert loader.client.auth == ('abc', '123')
