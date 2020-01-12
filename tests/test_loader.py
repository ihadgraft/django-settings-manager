from settings_manager import loader
import os
import pytest


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
