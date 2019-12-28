from settings_manager import loading
import os


def test_load_settings_files(settings_files):
    result = loading.load_settings_files(settings_files)
    assert os.path.basename(result[0]['_meta']['file']) == 'variables.yaml'
    assert os.path.basename(result[1]['_meta']['file']) == 'base.yml'
    assert os.path.basename(result[2]['_meta']['file']) == 'user.yaml'
