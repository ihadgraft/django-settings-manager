import re
import os
import yaml


def load_settings_files(settings_dirs):
    result = []
    for d in settings_dirs:
        for f in [os.path.join(d, n) for n in os.listdir(d)]:
            print(f)
            with open(f) as stream:
                data = yaml.load(stream, Loader=yaml.FullLoader)
            data.setdefault('_meta', {})
            data['_meta']['file'] = f
            result.append(data)

    return sorted(result, key=lambda e: e.get('_meta', {}).get('priority', 0))
