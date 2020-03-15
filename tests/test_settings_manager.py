import pytest
import settings_manager
import os


class TestSettingsWrapperGetValue(object):

    def test_valid(self, settings_test_helper):
        path = settings_test_helper.write({
            "configure": {
                "NAME": "john",
                "FAMILY": {"parents": {"father": "jim"}},
            }
        })
        sm = settings_manager.SettingsManager(path)
        settings_test_helper.configure(sm)
        w = settings_manager.SettingsWrapper(settings_test_helper.module)
        assert w.get_value_at_path('NAME') == 'john'
        assert w.get_value_at_path("FAMILY.parents.father") == 'jim'

    def test_missing_path(self, settings_test_helper):
        path = settings_test_helper.write({
            "configure": {
                "FAMILY": {"parents": {}},
            }
        })
        sm = settings_manager.SettingsManager(path)
        settings_test_helper.configure(sm)
        w = settings_manager.SettingsWrapper(settings_test_helper.module)
        with pytest.raises(settings_manager.InvalidPathError):
            assert w.get_value_at_path('NAME') == 'john'
        with pytest.raises(settings_manager.InvalidPathError):
            assert w.get_value_at_path("FAMILY.parents.father") == 'jim'

    def test_nondict_key(self, settings_test_helper):
        path = settings_test_helper.write({
            "configure": {
                "FAMILY": {"parents": []},
            }
        })
        sm = settings_manager.SettingsManager(path)
        settings_test_helper.configure(sm)
        w = settings_manager.SettingsWrapper(settings_test_helper.module)
        with pytest.raises(settings_manager.InvalidPathError, match="Value at path 'FAMILY.parents' is not a dict"):
            assert w.get_value_at_path("FAMILY.parents.father") == 'jim'


class TestSettingsWrapperSetValue(object):

    def test_set_value(self, settings_test_helper):
        path = settings_test_helper.write({
            "configure": {
                "NAME": "john",
                "FAMILY": {"parents": {"father": "jim"}},
            }
        })
        sm = settings_manager.SettingsManager(path)
        settings_test_helper.configure(sm)
        w = settings_manager.SettingsWrapper(settings_test_helper.module)
        w.set_value_at_path('NAME', 'bill')
        w.set_value_at_path('FAMILY.parents.father', 'bob')
        w.set_value_at_path('NAME2', 'phyllis')
        w.set_value_at_path('FAMILY2.parents.mother', 'rita')
        assert w.module.NAME == 'bill'
        assert w.module.FAMILY['parents']['father'] == 'bob'
        assert w.module.NAME2 == 'phyllis'
        assert w.module.FAMILY2['parents']['mother'] == 'rita'

    @pytest.mark.skip()
    def test_nondict_key(self, settings_test_helper):
        path = settings_test_helper.write({
            "configure": {
                "FAMILY": {"parents": []},
            }
        })
        sm = settings_manager.SettingsManager(path)
        settings_test_helper.configure(sm)
        w = settings_manager.SettingsWrapper(settings_test_helper.module)
        with pytest.raises(settings_manager.InvalidPathError, match="Value at path 'FAMILY.parents' is not a dict"):
            assert w.set_value_at_path("FAMILY.parents.father", "jim")


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
