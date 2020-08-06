from lib.plugins.notification import Notification
import requests


class Webhook(Notification):
    def notify(self, message: str):
        res = requests.post(self.url,
                            json={'message', message},
                            )


def setup():
    return Webhook
