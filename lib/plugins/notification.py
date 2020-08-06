class Notification(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def notify(self, message: str):
        raise NotImplementedError

    def isEnabled(self):
        return self.config.__dict__.get(self.__class__.__name__.lower())['enabled']
