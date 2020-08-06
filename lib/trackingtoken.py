from datetime import datetime
import logging
import json
import re
import requests
from .util import get_default_user_agent_string

log = logging.getLogger()


class TrackingToken:
    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.tags = list(self.config.tags)  # makes a new instance

        for k, v in kwargs.items():
            if k == 'tags':
                if type(v) == str:
                    self.tags.append(v)
                    self.tags = list(set(self.tags))
                elif type(v) == list:
                    self.tags = list(set(self.tags + v))
            else:
                setattr(self, k, v)

        self.value = self._get_token_from_server()

    def _get_token_from_server(self, payload='raw'):
        ctx = self._get_req_ctx(self.config.__dict__)
        ctx['payload'] = payload
        self.tags.sort()
        ctx['tags'] = self.tags
        res = requests.post('{0}://{1}/token'.format(self.config.token_protocol, self.config.token_server),
                            json=json.dumps(ctx),
                            headers={'User-Agent': get_default_user_agent_string(),
                                     'X-API-Key': self.config.server_api_key
                                     })

        token = res.json()['token']
        return token

    def _get_req_ctx(self, ctx):
        req_ctx = {}
        for k in ctx.keys():
            if 'token' in k or 'tags' == k or 'payload' == k:
                req_ctx[k] = ctx[k]

        return req_ctx

    def gen_url(self):
        return '{0}://{1}/{2}'.format(self.config.token_protocol, self.config.token_domain, self.value)

    def full_token(self):
        return "%s.%s" % (self.value, self.config.token_domain)

    @staticmethod
    def get_token_re_pattern(self, token_length):
        return re.compile(br'^(?P<token>[a-zA-Z0-9]{%s})' % bytes(token_length))
