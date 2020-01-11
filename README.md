# Settings Manager

This project provides a simple and extensible strategy for managing Django settings in distributed YAML files.

## Settings files

The settings manager takes a list of directories and loads all *.yaml or *.yml files in them.  To control the order of loading, set _meta.priority.  For example:

```yaml
_meta:
  priority: 10
```

Generally, it might be useful to set all files providing variables to a priority of zero, set base configuration file to 10, and local configuration overrides to 20.  For example:

```yaml
--- 
# variables.yml
_meta:
  priority: 0

---
# base.yml
DEBUG: false

---
# local.yml
DEBUG: true
```

## Settings and Variables

Settings are Django settings that get applied to the module and would traditionally be set in settings.py.  Variables are configuration variables that are useful for parameterizing configurations, or for getting external values using a handler.

Settings and variables in YAML can be specified directly, such as:

```yaml
variables:
  db_user: postgres

settings:
  DEBUG: false
```

Or they can be provided by a registered handler. The following example gets the value of the environment variable `DJANGO_DB_PASSWORD` and assigns it to the configuration variable `db_password`.

```yaml
variables:
  db_password:
    _handlers:
      - name: get_env
        kwargs: {key: DJANGO_DB_PASSWORD}
```

## Interpolating variables

Now, the password can be used with:

```yaml
settings:
  DATABASES:
    default:
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
loader.handlers['get_random'] = GetRandomHandler() 
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
