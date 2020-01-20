from settings_manager import handler
import pytest
import os


class TestEnvironmentVariableHandler(object):

    def test_with_value(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'FOO', 'bar')
        h = handler.EnvironmentVariableHandler()
        assert h.get_value({}, key='FOO') == 'bar'

    def test_without_value_with_default(self):
        h = handler.EnvironmentVariableHandler()
        assert h.get_value({}, key='FOO', default='bar') == 'bar'

    def test_without_value_without_default(self):
        h = handler.EnvironmentVariableHandler()
        with pytest.raises(KeyError, match='is not defined in environment'):
            h.get_value({}, key='FOO')


class TestFileHandler(object):

    def test_str(self, file_handler_data):
        h = handler.FileVariableHandler()
        assert h.get_value({}, file=file_handler_data['string.txt']['path'], parser='str') == 'foo\n\n'

    def test_str_trimmed(self, file_handler_data):
        h = handler.FileVariableHandler()
        assert h.get_value({}, file=file_handler_data['string.txt']['path'], parser='str_trimmed') == 'foo'

    def test_int(self, file_handler_data):
        h = handler.FileVariableHandler()
        assert type(h.get_value({}, file=file_handler_data['int.txt']['path'], parser='int')) is int

    def test_float(self, file_handler_data):
        h = handler.FileVariableHandler()
        assert type(h.get_value({}, file=file_handler_data['int.txt']['path'], parser='float')) is float

    def test_yaml(self, file_handler_data):
        h = handler.FileVariableHandler()
        assert h.get_value({}, file=file_handler_data['dict.yml']['path'], parser='yaml') == {'value': 1}

    def test_json(self, file_handler_data):
        h = handler.FileVariableHandler()
        assert h.get_value({}, file=file_handler_data['dict.json']['path'], parser='json') == {'value': 1}
