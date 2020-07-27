import hvac
import os
from .secret import AbstractSecretLoader


class AbstractVaultReader(object):
    def read(self, client: hvac.Client, *args, **kwargs) -> dict:
        raise NotImplementedError


class VaultKVV1Reader(AbstractVaultReader):
    def read(self, client: hvac.Client, *args, **kwargs) -> dict:
        return client.secrets.kv.v1.read_secret(*args, **kwargs)


class VaultKVV2Reader(AbstractVaultReader):
    def read(self, client: hvac.Client, *args, **kwargs) -> dict:
        return client.secrets.kv.v2.read_secret_version(*args, **kwargs)


class AbstractVaultSecretLoader(AbstractSecretLoader):
    client = None  # type: hvac.Client

    def __init__(self, reader: AbstractVaultReader):
        self.reader = reader

    def get_addr(self, settings: dict):
        try:
            return os.environ['VAULT_ADDR']
        except KeyError:
            return settings['VAULT_ADDR']

    def _init_client(self, settings: dict):
        raise NotImplementedError

    def resolve(self, settings: dict) -> dict:
        secrets = {}
        if self.client is None:
            self._init_client(settings)
        for k, conf in settings.get('VAULT_SECRETS', {}).items():
            if isinstance(conf, str):
                conf = {'path': conf}
            secrets[k] = self.reader.read(self.client, **conf)
        return secrets


class VaultAppRoleSecretLoader(AbstractVaultSecretLoader):
    client_cls = hvac.Client

    def get_role_id(self, settings: dict):
        try:
            return os.environ['VAULT_ROLE_ID']
        except KeyError:
            return settings['VAULT_ROLE_ID']

    def get_secret_id(self, settings: dict):
        return os.environ['VAULT_SECRET_ID']

    def _init_client(self, settings: dict):
        self.client = self.client_cls(self.get_addr(settings))
        self.client.auth_approle(
            self.get_role_id(settings),
            self.get_secret_id(settings),
        )
