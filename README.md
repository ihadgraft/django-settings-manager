# Settings Manager

This project provides a simple and extensible strategy for managing Django settings.  

## Settings file format

There are three main sections:

* **configure** - This is intended to be set up before most processing in settings.py, and should mostly be used to enable/disable built-in features. For example, settings.py might configure remote user auth if ENABLE_REMOTE_USER_AUTH is true.
* **override** - This is used to override settings.py.  Use this section for database settings and other more complex configurations that are environment specific.
* **inject** - This is used to override values using one of the built-in fuctions, or any user-defined function that is made available.

## Example settings.py file

```python
import sys
import os
from settings_manager import SettingsManager


settings_manager = SettingsManager(os.environ.get("DJANGO_SETTINGS_FILE", "/etc/django-settings.yaml"))

# Defaults for configurable items
ENABLE_REMOTE_USER_AUTH = False
ENABLE_MODEL_AUTH = False

# Configure settings manager
settings_manager.configure(sys.modules[__name__])

# Set the module's base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend' if ENABLE_MODEL_AUTH else None,
    'shibboleth.backends.ShibbolethRemoteUserBackend' if ENABLE_REMOTE_USER_AUTH else None,
]

# ... other configuration ...

# Rebuild AUTHENTICATION_BACKENDS to remove null values
AUTHENTICATION_BACKENDS = [m for m in AUTHENTICATION_BACKENDS if m is not None]

settings_manager.override(sys.modules[__name__])
```

## Sample configuration (YAML) file

```yaml
inject:
  DATABASES.default.password:
    function: get_env
    args: [DJANGO_DATABASE_PASSWORD]
  
  DEBUG:
    function: get_env
    args: [DJANGO_DEBUG]
    value_processors:
      - function: str_to_bool
        args: ['<<value>>']

configure:
  ENABLE_REMOTE_USER_AUTH: true
 
override:
  DATABASES:
    default:
      username: django
      name: django
      host: db
      port: 5432
      password: ~  # will be replaced by injected value.
```
