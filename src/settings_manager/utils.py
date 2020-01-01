import copy
import os
import re

import yaml


def _list_files(dir_list, match=None):
    for dir_path in dir_list:
        return (
            os.path.join(dir_path, p) for p in os.listdir(dir_path)
            if (match is None) or (re.search(match, p) is not None)
        )


def load_files(dir_list):
    files = []
    for file in _list_files(dir_list, r"\.ya?ml$"):
        with open(file) as stream:
            data = yaml.load(stream, Loader=yaml.FullLoader)
        files.append((file, data))
    return sorted(files, key=lambda e: e[1].get('_meta', {}).get('priority', 0))


def merge_values(destination, source):
    result = copy.deepcopy(destination)
    for k in source:
        if isinstance(source[k], dict) and k in result and isinstance(result[k], dict):
            result[k] = merge_values(result[k], source[k])
        else:
            result[k] = source[k]
    return result


def substitute_variables(item, variables):
    if isinstance(item, dict):
        return {k: substitute_variables(item[k], variables) for k in item}
    elif isinstance(item, list):
        return [substitute_variables(v, variables) for v in item]
    elif isinstance(item, str):
        m = re.match(r"^{(?P<name>[^}]+)}$", item)
        if m is not None:
            return variables[m.group('name')]
        else:
            return item % variables
    else:
        return item
