from lib.plugins.notification import Notification
import requests


class Mailgun(Notification):
    def notify(self, message: str):
        res = requests.post(
            f'https://api.mailgun.net/v3/{self.config.mailgun["domain"]}/messages',
            auth=("api", self.config.mailgun["api_key"]),
            data={"from": self.config.mailgun["from"],
                  "to": [self.config.mailgun["to"]],
                  "subject": self.config.mailgun["subject"],
                  "text": message})
        print(res.content)
        return res


def setup():
    return Mailgun
