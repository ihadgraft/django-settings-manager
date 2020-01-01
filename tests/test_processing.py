from settings_manager import processing
import pytest


class TestStringToBoolProcessor(object):

    def test_true(self):
        p = processing.ValueToBoolProcessor()
        assert p.process_value('a', {})

    def test_false(self):
        p = processing.ValueToBoolProcessor()
        assert not p.process_value(' ', {})

    def test_non_string(self):
        p = processing.ValueToBoolProcessor()
        with pytest.raises(processing.ProcessingError, match="Value is not a string"):
            assert not p.process_value(['a'], {})


class TestValueSubstitutionProcessor(object):

    def test_get_value(self):
        value = {
            "name": "%(value)s",
            "options": [
                {"value": "%(value)s"},
                {"value": "%(bar_value)s"},
            ]
        }
        p = processing.VariableSubstitutionProcessor()
        assert p.process_value(value, {"value": "foo", "bar_value": "bar"}) == {
            "name": "foo",
            "options": [
                {"value": "foo"},
                {"value": "bar"}
            ]
        }
