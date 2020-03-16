import pytest
import tempfile
import os
import yaml
from types import ModuleType


@pytest.fixture()
def settings_test_helper(monkeypatch):

    class _ConfigTestHelper(object):
        config_file = None
        module = None

        def __init__(self):
            self.module = ModuleType('__test_module__')

        def configure(self, cm):
            cm.configure(self.module)
            return self.module

        def override(self, cm):
            cm.override(self.module)
            return self.module

        def write(self, data):
            temp_dir = tempfile.mkdtemp()
            self.config_file = os.path.join(temp_dir, 'config.yaml')

            with open(self.config_file, 'w') as stream:
                yaml.dump(data, stream)

            return self.config_file

    return _ConfigTestHelper()
