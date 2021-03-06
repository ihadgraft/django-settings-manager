import pytest
import settings_manager
import os
from types import ModuleType


class MockModule(ModuleType):
    NAME = None  # type: str
    DATA = None  # type: dict

    def __init__(self):
        super().__init__('__mock_module__')
        self.NAME = 'john'
        self.DATA = {
            'age': 32,
            'tags': ['scholar', 'gentleman']
        }


class TestGetAccessorFunctions(object):

    def test_module_get(self):
        module = MockModule()
        _get, _set = settings_manager.get_accessor_functions(module)
        assert _get('NAME') == 'john'

    def test_module_set(self):
        module = MockModule()
        _get, _set = settings_manager.get_accessor_functions(module)
        _set('NAME', 'bill')
        assert module.NAME == 'bill'

    def test_dict_get(self):
        module = MockModule()
        _get, _set = settings_manager.get_accessor_functions(module.DATA)
        assert _get('age') == 32

    def test_dict_set(self):
        module = MockModule()
        _get, _set = settings_manager.get_accessor_functions(module.DATA)
        _set('age', 40)
        assert module.DATA['age'] == 40


class TestGetValueForPath(object):

    def test_exists(self):
        module = MockModule()
        assert settings_manager.get_value_for_path(module, 'NAME') == 'john'
        assert settings_manager.get_value_for_path(module, 'DATA.age') == 32

    def test_not_exists(self):
        module = MockModule()
        with pytest.raises(settings_manager.InvalidPathError, match="Value not valid at 'POSITION'"):
            settings_manager.get_value_for_path(module, 'POSITION')
        with pytest.raises(settings_manager.InvalidPathError, match="Value not valid at 'DATA.position'"):
            settings_manager.get_value_for_path(module, 'DATA.position')


class TestSetValueForPath(object):

    def test_ovewrite(self):
        module = MockModule()
        settings_manager.set_value_for_path(module, 'NAME', 'bill')
        settings_manager.set_value_for_path(module, 'DATA.age', 40)
        assert module.NAME == 'bill'
        assert module.DATA['age'] == 40

    def test_new(self):
        module = MockModule()
        settings_manager.set_value_for_path(module, 'POSITION', 'A')
        settings_manager.set_value_for_path(module, 'TREE.branch', 'B')
        assert getattr(module, 'POSITION') == 'A'
        assert getattr(module, 'TREE')['branch'] == 'B'

    def test_nondict_key(self):
        module = MockModule()
        with pytest.raises(settings_manager.InvalidPathError, match="Not a dict or module at path 'DATA.tags'"):
            settings_manager.set_value_for_path(module, 'DATA.tags.scholar', 'test')


def test_config_manager(settings_test_helper):
    path = settings_test_helper.write({
        "configure": {
            "NAME": "john",
        }
    })

    cm = settings_manager.SettingsManager(path)
    module = settings_test_helper.configure(cm)
    assert getattr(module, "NAME") == "john"


def test_env_override(settings_test_helper, monkeypatch):
    path = settings_test_helper.write({
        "inject": {
            "DATABASES.default.PASSWORD": {
                "function": "get_env",
                "args": ["DJANGO_DATABASE_PASSWORD"]
            },

            "STATIC_PATH": {
                "function": "get_env",
                "args": ["DJANGO_STATIC_PATH"]
            },

            "TRUE_STRING": {
                "function": "get_env",
                "args": ["DJANGO_TRUE_STRING"],
                "value_processors": [{
                    "function": "str_to_bool",
                    "args": ["<<value>>"],
                }]
            },

            "FALSE_STRING": {
                "function": "get_env",
                "args": ["DJANGO_FALSE_STRING"],
                "value_processors": [{
                    "function": "str_to_bool",
                    "args": ["<<value>>"],
                }]
            }
        }
    })
    cm = settings_manager.SettingsManager(path)
    monkeypatch.setitem(os.environ, "DJANGO_DATABASE_PASSWORD", "test1234")
    monkeypatch.setitem(os.environ, "DJANGO_STATIC_PATH", "/app/static")
    monkeypatch.setitem(os.environ, "DJANGO_TRUE_STRING", "True")
    monkeypatch.setitem(os.environ, "DJANGO_FALSE_STRING", "False")
    module = settings_test_helper.override(cm)
    assert getattr(module, "DATABASES")['default']['PASSWORD'] == 'test1234'
    assert getattr(module, "STATIC_PATH") == '/app/static'
    assert getattr(module, "TRUE_STRING") and (type(getattr(module, "TRUE_STRING")) is bool)
    assert (not getattr(module, "FALSE_STRING")) and (type(getattr(module, "FALSE_STRING")) is bool)
