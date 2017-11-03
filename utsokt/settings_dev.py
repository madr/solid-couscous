from .settings import *

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

try:
    env_file = os.environ.get('UTSOKT_ENV_JSON', 'env.json')
    path = os.path.join(PROJECT_PATH, env_file)
    with open(path) as f:
        env = json.load(f)
except IOError as e:
    if e.errno == 2:
        msg = 'Unable to find "{file}" at "{path}"!'
        print(msg.format(path=path, file=env_file))
        sys.exit(1)
    else:
        raise e

SLACK_CLIENT_ID = env['dev'].get('slack_client_id', None)
SLACK_CLIENT_SECRET = env['dev'].get('slack_client_secret', None)
