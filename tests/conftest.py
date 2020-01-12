import pytest
import tempfile
import os


@pytest.fixture()
def settings_files():
    result = []
    root = tempfile.mkdtemp()

    def _save(dirname, filename, text):
        os.mkdir(os.path.join(root, dirname))
        with open(os.path.join(root, dirname, filename), 'w') as stream:
            stream.write(text)
        result.append(os.path.join(root, dirname))

    y = """
    _meta: {priority: 0}

    variables:
        db_name: mydb
        db_password:
            _handlers:
                - name: get_env
                  kwargs: {key: DJANGO_DB_PASSWORD}
    """
    _save('variables', 'variables.yaml', y)

    y = """
    _meta: {priority: 10}
    settings:
        DEBUG: false
        DATABASES:
            default:
                NAME: '{db_name}'
                PASSWORD: '{db_password}'
    """
    _save('base', 'databases.yml', y)

    y = """
    _meta: {priority: 20}
    settings:
        DEBUG: true
    """
    _save('user', 'user.yaml', y)
    return result
