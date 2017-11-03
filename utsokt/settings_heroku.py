import dj_database_url

from .settings import *

SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID', None)
SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET', None)
DATABASES['default'].update(dj_database_url.config(conn_max_age=500))
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'example.com').split()
DEBUG = bool(os.environ.get('DEBUG', '0'))
