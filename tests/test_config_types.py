from settings_manager import config_types
import pytest


class TestGetConfigItem(object):

    def test_no_type_specified(self):
        result = isinstance(
            config_types.get_config_item("string"),
            config_types.DefaultConfigType
        )
        assert result, "Type is DefaultConfigType"

    def test_type_specified(self):
        result = isinstance(
            config_types.get_config_item({"_type": "settings_manager.config_types.ValueLookupConfigType"}),
            config_types.ValueLookupConfigType
        )
        assert result, "Type is EnvVariableType"


class TestConfigTypeBase(object):

    def test_get_value(self):
        class _ConfigType(config_types.ConfigTypeBase):
            def _get_raw_value(self, context):
                return {
                    "string": "%(value)s",
                    "list": [
                        {"value": "%(value)s"}
                    ]
                }

        item = _ConfigType("")
        assert item.get_value({"value": "foo"}) == {
            "string": "foo",
            "list": [
                {"value": "foo"}
            ]
        }


class TestDictConfigType(object):
    context = None  # type: dict

    def setup(self):
        self.context = {"env": {"value": "foo"}}

    def test_valid(self):
        conf = {
            "key": "value",
            "source": "env",
        }
        item = config_types.ValueLookupConfigType(conf)
        assert item.get_value(self.context) == "foo"

    def test_key_not_provided(self):
        conf = {
            "source": "env",
        }
        item = config_types.ValueLookupConfigType(conf)
        with pytest.raises(config_types.ConfigError, match=r"must provide a value for 'key'"):
            item.get_value(self.context)

    def test_source_not_provided(self):
        conf = {
            "key": "value",
        }
        item = config_types.ValueLookupConfigType(conf)
        assert item.get_value(self.context) == "foo"

    def test_source_not_defined_in_context(self):
        conf = {
            "key": "value",
            "source": "missing",
        }
        item = config_types.ValueLookupConfigType(conf)
        with pytest.raises(config_types.ConfigError, match=r"'source' value doesn't exist in context"):
            item.get_value(self.context)

    def test_value_missing_with_default(self):
        conf = {
            "key": "missing",
            "source": "env",
            "default": "foo",
        }
        item = config_types.ValueLookupConfigType(conf)
        assert item.get_value(self.context) == "foo"

    def test_value_missing_without_default(self):
        conf = {
            "key": "missing",
            "source": "env",
        }
        item = config_types.ValueLookupConfigType(conf)
        with pytest.raises(config_types.ConfigError, match='no default is provided'):
            item.get_value(self.context)

