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
    
    db_name:
      _meta:
        type: variable
        processors:
          - name: settings_manager.processor.GetEnv
            kwargs: {default: postgres_user}
      _value: DJANGO_DB_USER
      
    db_password:
      _meta:
        type: variable
        processors:
          - name: settings_manager.processor.GetEnv
      _value: DJANGO_DB_PASSWORD
    """
    _save('variables', 'variables.yaml', y)

    y = """
    _meta: {priority: 10}
    DEBUG: false
    """
    _save('base', 'base.yml', y)

    y = """
    _meta: {priority: 20}
    DEBUG: true
    DATABASES:
      default:
        ENGINE: django.db.backends.postgresql
        NAME: '%(db_name)s'
        PASSWORD: '%(db_password)s'
    """
    _save('user', 'user.yaml', y)
    return result
