import os


def get_version():
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', 'VERSION')).read().strip()


def get_default_user_agent_string():
    return 'mole v%s' % get_version()


def token_from_hostname(hostname):
    return hostname.split('.')[-3]
