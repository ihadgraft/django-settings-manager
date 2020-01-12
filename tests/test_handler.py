from settings_manager import loader
import pytest
import os


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


