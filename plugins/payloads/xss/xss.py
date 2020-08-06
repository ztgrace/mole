from lib.plugins.listpluginmixin import ListPluginMixin
import os


class XSS(ListPluginMixin):
    description = "XSS Payloads"

    def __init__(self, *args, **kwargs):
        super(ListPluginMixin, self).__init__(*args, **kwargs)
        self.name = 'XSS'
        self.list = 'xss.txt'
        self.path = os.path.abspath(os.path.dirname(__file__))

    def test(self):
        pass


def setup(servers, payloads):
    payloads['xss'] = XSS
