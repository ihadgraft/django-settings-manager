import copy
import re

import yaml


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

