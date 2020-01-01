import os


class HandlerValueNotProvided(Exception):
    pass


class Argument(object):
    name = None  # type: str
    required = None  # type: bool
    help_text = None  # type: str

    def __init__(self, name, help_text='', required=False):
        self.name = name
        self.required = required
        self.help_text = help_text


def handler(help_text='', kwargs=None):
    if kwargs is None:
        kwargs = []

    def _wrapper(target):
        target.help_text = help_text
        target.kwargs = kwargs
        return target
    return _wrapper


@handler(
    help_text="Get databases",
    kwargs=[Argument("db_password", "The database password", True)]
)
def get_databases(db_password=None):
    return {
        "default": {
            "ENGINE": "",
            "PASSWORD": db_password,
        }
    }


@handler(
    help_text="Get a variable from the environment",
    kwargs=[Argument("key", "The name of the environment variable", True)],
)
def get_env(key=None):
    if key in os.environ:
        return os.environ[key]
    raise HandlerValueNotProvided("Environment variable %s is not defined" % key)
