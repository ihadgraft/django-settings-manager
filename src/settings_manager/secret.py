class SecretError(Exception):
    pass


class AbstractSecretLoader(object):

    def resolve(self, settings: dict) -> dict:
        """
        Resolve secrets.

        @param settings: The settings.
        @return A dictionary of values loaded from the secret provider.
        """
        raise NotImplementedError
