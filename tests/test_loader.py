from settings_manager import loader
import os
import pytest


class TestEnvironmentVariableHandler(object):

    def test_with_value(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'FOO', 'bar')
        h = loader.EnvironmentVariableHandler()
        assert h.get_value({}, key='FOO') == 'bar'

    def test_without_value_with_default(self):
        h = loader.EnvironmentVariableHandler()
        assert h.get_value({}, key='FOO', default='bar') == 'bar'

    def test_without_value_without_default(self):
        h = loader.EnvironmentVariableHandler()
        with pytest.raises(KeyError, match='is not defined in environment'):
            h.get_value({}, key='FOO')


class TestConfigLoader(object):

    def test_load(self, settings_files, monkeypatch):
        monkeypatch.setitem(os.environ, "DJANGO_DB_PASSWORD", "pass")

        class Module(object):
            pass

        module = Module()
        config_loader = loader.ConfigLoader(module)
        config_loader.load(settings_files)
        assert module.DEBUG
        assert module.DATABASES == {
            "default": {
                "NAME": "mydb",
                "PASSWORD": "pass"
            }
        }
