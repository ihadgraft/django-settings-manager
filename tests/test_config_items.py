from settings_manager import config_items, processing
import pytest


class MockValueProcessor(processing.ValueProcessorBase):

    def process_value(self, value, context):
        return {
            **value,
            **{"extra": "bar"}
        }


class TestConfigItemBase(object):

    def test_get_value(self):

        class _ConfigItem(config_items.ConfigItemBase):
            def _get_raw_value(self, context):
                return {
                    "string": "%(value)s",
                }
        item = _ConfigItem({"_processors": ["%s.MockValueProcessor" % MockValueProcessor.__module__]})
        assert item.get_value({"value": "foo"}) == {
            "string": "foo",
            "extra": "bar",
        }


class TestDictConfigItem(object):
    context = None  # type: dict

    def setup(self):
        self.context = {"env": {"value": "foo"}}

    def test_non_root_context_value(self):
        conf = {
            "key": "value",
            "context_key": "env",
        }
        item = config_items.ValueLookupConfigItem(conf)
        assert item.get_value(self.context) == "foo"

    def test_root_context_value(self):
        conf = {
            "key": "value",
        }
        self.context["value"] = "foo"
        item = config_items.ValueLookupConfigItem(conf)
        assert item.get_value(self.context) == "foo"

    def test_key_not_provided(self):
        conf = {
            "context_key": "env",
        }
        item = config_items.ValueLookupConfigItem(conf)
        with pytest.raises(config_items.ConfigError, match=r"must provide a value for 'key'"):
            item.get_value(self.context)

    def test_context_key_not_defined_in_context(self):
        conf = {
            "key": "value",
            "context_key": "missing",
        }
        item = config_items.ValueLookupConfigItem(conf)
        with pytest.raises(config_items.ConfigError, match=r"Context lookup failed with context_key"):
            item.get_value(self.context)

    def test_value_missing_and_default_provided(self):
        conf = {
            "key": "missing",
            "context_key": "env",
            "default": "foo",
        }
        item = config_items.ValueLookupConfigItem(conf)
        assert item.get_value(self.context) == "foo"

    def test_value_missing_and_no_default_provided(self):
        conf = {
            "key": "missing",
            "context_key": "env",
        }
        item = config_items.ValueLookupConfigItem(conf)
        with pytest.raises(config_items.ConfigError, match='no default is provided'):
            item.get_value(self.context)

