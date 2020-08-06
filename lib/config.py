import os
import sys
import yaml


class Config(object):
    def __init__(self, conf_file='config.yml'):
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', conf_file)
        conf = open(self.path, 'r').read()

        # Support Python 2 and 3 for Burp
        if float(sys.version[0:3]) >= 3.0:
            conf = yaml.safe_load(conf)
        else:
            conf = yaml.load(conf)

        # Token config
        self.token_domain = conf['token']['domain']
        self.token_length = int(conf['token']['length'])
        if conf['token']['ssl']:
            self.token_protocol = 'https'
        else:
            self.token_protocol = 'http'
        self.token_server = conf['token']['server']
        self.tags = conf['token']['default_tags']

        # Server config
        self.server_web_port = conf['server']['web_port']
        self.server_dns_port = conf['server']['dns_port']
        self.server_db_conn = conf['server']['db_conn']
        self.server_api_key = conf['server']['api_key']
        self.dns_addr = conf['server']['dns_addr']
        self.static_responses = conf['server'].get('static_responses', list())

        # Mailgun

        self.mailgun = conf['notifications']['mailgun']

        # Slack
        self.slack = conf['notifications']['slack']

        # Webhook
        self.webhook = conf['notifications']['webhook']


        self.debug = False
        self.output = 'output'
        self.notifications = list()
