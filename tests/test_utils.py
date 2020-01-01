from settings_manager import utils


class TestMergeValues(object):

    def test_merge(self):
        d = {"person": {"name": "john"}}
        s = {"person": {"age": 22}}
        assert utils.merge_values(d, s) == {"person": {"name": "john", "age": 22}}

