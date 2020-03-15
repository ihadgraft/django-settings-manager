import settings_manager
import os


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
            "DATABASES.default.PASSWORD": ["get_env", ["DJANGO_DATABASE_PASSWORD"], {}],
            "STATIC_PATH": ["get_env", ["DJANGO_STATIC_PATH"], {}],
        }
    })
    cm = settings_manager.SettingsManager(path)
    monkeypatch.setitem(os.environ, "DJANGO_DATABASE_PASSWORD", "test1234")
    monkeypatch.setitem(os.environ, "DJANGO_STATIC_PATH", "/app/static")
    module = settings_test_helper.override(cm)
    assert getattr(module, "DATABASES")['default']['PASSWORD'] == 'test1234'
    assert getattr(module, "STATIC_PATH") == '/app/static'
