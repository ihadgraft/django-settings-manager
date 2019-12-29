import pytest
from settings_manager import loading
import os


def item_processor(value, **kwargs):
    return '%s_%s' % (value, kwargs['default'])


def test_load_settings_files(settings_files):
    result = loading.load_settings_files(settings_files)
    assert os.path.basename(result[0]['_meta']['file']) == 'variables.yaml'
    assert os.path.basename(result[1]['_meta']['file']) == 'base.yml'
    assert os.path.basename(result[2]['_meta']['file']) == 'user.yaml'


class TestConfigurationItemType(object):

    def test_not_set(self):
        i = loading.ConfigurationItem("FOO_SETTING", {})
        assert i.type == 'setting'

    def test_set(self):
        i = loading.ConfigurationItem("FOO_SETTING", {
            "_meta": {"type": "variable"}
        })
        assert i.type == 'variable'

    def test_set_invalid(self):
        with pytest.raises(loading.InvalidConfigurationItemType):
            loading.ConfigurationItem("FOO_SETTNG", {
                "_meta": {"type": "invalid"}
            })


class TestConfigurationItemGetValue(object):

    def test_processors(self):
        i = loading.ConfigurationItem('FOO_SETTING', {
            "_meta": {
                "processors": [
                    {
                        "name": "tests.test_loading.item_processor",
                        "kwargs": {"default": "bar"},
                    },
                    {
                        "name": "tests.test_loading.item_processor",
                        "kwargs": {"default": "baz"},
                    }
                ]
            },
            "_value": "foo"
        })
        assert i.value == "foo_bar_baz"

    def test_value(self):
        i = loading.ConfigurationItem("FOO_SETTING", {}, {"item": "foo"})
        assert i.value == {"item": "foo"}


def test_apply_context():
    value = {
        "list": [
            {"value": "%(value)s"},
        ],
    }
    assert loading.apply_context(value, {"value": "foo"}) == {"list": [{"value": "foo"}]}


class TestParseSettingsData(object):

    def test_parse(self):
        data = {
            "a_value": {
                "_meta": {
                    "type": "variable",
                },
                "_value": "a",
            },

            "setting_a": "%(a_value)s",
            "setting_b": "%(b_value)s",
        }
        assert (loading.parse_settings_data(data, {"b_value": "b"}) == {"setting_a": "a", "setting_b": "b"})

