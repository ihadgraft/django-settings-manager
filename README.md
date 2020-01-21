# Settings Manager

This project provides a simple and extensible strategy for managing Django settings in YAML files that can be loaded from multiple locations and prioritized. This makes it easy to provide application configuration that the user can override or extend for a specific environment without having to depend on Python.  This is very useful for containerized environments (e.g. docker-compose, OpenShift/OKD) where configuration values may be derived from multiple places.  

The settings manager takes a list of directories and loads all *.yaml or *.yml files in them.  

## Settings file format

To control the order of loading, set _meta.priority.  For example:

```yaml
_meta:
  priority: 10
```

Generally, it will be useful to set all files providing variables to a low priority, set base configuration file to a higher priority, and local configuration overrides to the highest priority.  For example:

```yaml
--- 
# variables.yml
_meta: {priority: 0}
variables:
  db_name: my_database

---
# base.yml
_meta: {priority: 10}
settings:
  DEBUG: false

---
# local.yml
_meta: {priority: 20}
settings:
  DEBUG: true
  DATABASE_NAME: '{db_name}'
```

## Settings and Variables sections

Settings are Django settings that get applied to the module and would traditionally be set in settings.py.  Variables are useful for parameterizing configurations, or for getting external values using a handler.

Settings and variables in YAML can be specified directly, such as:

```yaml
variables:
  db_user: postgres

settings:
  DEBUG: false
```

Or they can be provided by a registered handler. The following example gets the value of the environment variable `DJANGO_DB_USER` and assigns it to the configuration variable `db_user`. Then, it loads the contents of `/var/run/secrets/db-password` into the variable `db_password`.

```yaml
variables:
  db_user:
    _handlers:
      - name: get_env
        kwargs: {key: DJANGO_DB_USER}
  db_password:
    _handlers:
      - name: get_file
        kwargs: {file: /var/run/secrets/db-password}
```

## Interpolating variables

Now, the password set above can be used with:

```yaml
settings:
  DATABASES:
    default:
      USER: '{db_user}'
      PASSWORD: '{db_password}'
```

## Handlers

Handlers process data and return a value that gets assigned, typically to a setting. Custom handlers can be registered by extending the AbstractConfigHandler class and registering an instance of the class like this:

```yaml

class GetRandomHandler(AbstractConfigHandler):
    def get_value(self, context, **kwargs):
        return rand(kwargs['min'], kwargs['max'])

class AsStringHandler(AbstractConfigHandler):
    def get_value(self, context, **kwargs):
        return str(kwargs['value'])

loader = ConfigLoader()
loader.handlers.update({
    'get_random': GetRandomHandler(),
    'as_string': AsStringHandler(),
})

```

In Yaml, the following could use the custom handlers to generate a random number and provide it as a string value.

```yaml
settings:
  RANDOM_VALUE:
    _handlers:
      - name: get_random
        kwargs: {min: 0, max: 5}
      - name: as_string
```

## Implementation in a Django project

The following code loads all yaml files from the `./conf` directory, plus any files specified by the `DJANGO_CONFIG_PATHS` environment variable.

For the example, the assumed file structure is:

```text
django-myproject/
  src/
    /myproject
      conf/
      /settings.py
  setup.py
```

```python
# File: settings.py
import sys
import os
from settings_manager.loader import ConfigLoader


# Set the module's base directory
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Set the default configuration directory
DEFAULT_CONF_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "conf")

# Create the loader
loader = ConfigLoader(sys.modules[__name__])

# Load all yaml files from comma-separated list of directories provided by environment variable 'DJANGO_CONFIG_PATHS'.
paths = [p.strip() for p in os.environ.get("DJANGO_CONFIG_PATHS", "").split(',') if p != '']

# Insert the base settings directory into the config paths.
paths.insert(0, DEFAULT_CONF_DIR)

# If providing additional / custom handlers, register them here
# loader.handlers.update({
#     "my_custom_handler": MyCustomHandler(),
# })

# Load the configuration.
loader.load(paths)
```
