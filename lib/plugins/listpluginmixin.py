import os
import re
from .plugin import Plugin
from ..trackingtoken import TrackingToken


class ListPluginMixin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build(self):
        payloads = list()
        i = 0

        # Loop through the files in the configured directory
        with open(os.path.join(self.path, self.list), 'r') as fin:
            for line in fin:
                line = line.strip()
                if not re.match(r'^#', line) and not re.match(r'^$', line):
                    tags = [self.name, '{}-payloads{}'.format(self.list, i)]
                    t = TrackingToken(config=self.config, tags=tags)
                    payload = line.replace('<TOKEN>', t.value)
                    payload = payload.replace('<DOMAIN>', t.config.token_domain)
                    payload = payload.replace('<PROTO>', t.config.token_protocol)
                    payloads.append(payload)
                    i += 1

        return payloads
