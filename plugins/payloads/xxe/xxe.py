from lib.plugins.listpluginmixin import ListPluginMixin
import os


class XXE(ListPluginMixin):
    description = "XXE Payloads"

    def __init__(self, *args, **kwargs):
        super(ListPluginMixin, self).__init__(*args, **kwargs)
        self.name = 'XXE'
        self.list = 'xxe.txt'
        self.path = os.path.abspath(os.path.dirname(__file__))


def setup(servers, payloads):
    payloads['xxe'] = XXE
