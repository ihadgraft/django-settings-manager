import os
import re


def list_files(dir_list, match=None):
    for dir_path in dir_list:
        return (
            os.path.join(dir_path, p) for p in os.listdir(dir_path)
            if (match is None) or (re.search(match, p) is not None)
        )
