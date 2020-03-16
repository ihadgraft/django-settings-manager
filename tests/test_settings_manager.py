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


class TestPathSearch(object):

    def test_get(self):
        ps = settings_manager.PathSearch(MockModule())
        assert ps.get("NAME") == "john"
        assert ps.get("DATA.age") == 32
        assert ps.get("DATA.tags") == ['scholar', 'gentleman']

    def test_get_nondict_key(self):
        ps = settings_manager.PathSearch(MockModule())
        with pytest.raises(settings_manager.InvalidPathError, match="Can't traverse through a non-dict at 'DATA.tags'"):
            ps.get('DATA.tags.scholar')

    def test_set_existing_path(self):
        m = MockModule()
        ps = settings_manager.PathSearch(m)
        ps.set('NAME', 'bill')
        ps.set('DATA.age', 44)
        assert m.NAME == 'bill'
        assert m.DATA['age'] == 44

    def test_set_nondict_key(self):
        m = MockModule()
        ps = settings_manager.PathSearch(m)
        with pytest.raises(settings_manager.InvalidPathError, match="Can't traverse through a non-dict at 'DATA.tags'"):
            ps.set('DATA.tags.scholar', 'value')


def test_config_manager(settings_test_helper):
    path = settings_test_helper.write({
        "configure": {
            "NAME": "john",
        }
    })

    cm = settings_manager.SettingsManager(path)
    module = settings_test_helper.configure(cm)
    assert getattr(module, "NAME") == "john"


# def test_set_dict(settings_test_helper):
#     path = settings_test_helper.write({
#         "env": {
#             "DATABASES.default.PASSWORD": [
#                 {
#                     "function":
#                 }
#             ]
#         }
#     })
#     sm = settings_manager.SettingsManager(path)

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
        }
    })
    cm = settings_manager.SettingsManager(path)
    monkeypatch.setitem(os.environ, "DJANGO_DATABASE_PASSWORD", "test1234")
    monkeypatch.setitem(os.environ, "DJANGO_STATIC_PATH", "/app/static")
    module = settings_test_helper.override(cm)
    assert getattr(module, "DATABASES")['default']['PASSWORD'] == 'test1234'
    assert getattr(module, "STATIC_PATH") == '/app/static'
