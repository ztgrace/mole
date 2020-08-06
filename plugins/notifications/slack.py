from lib.plugins.notification import Notification
import requests


class Slack(Notification):
    def notify(self, message: str):
        data = {'channel': self.config.slack['channel'], 'text': message}
        res = requests.post('https://slack.com/api/chat.postMessage',
                            json=data,
                            headers={'Authorization': f'Bearer {self.config.slack["token"]}'},
                            )


def setup():
    return Slack
