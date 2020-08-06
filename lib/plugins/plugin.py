class Plugin(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def build(self):
        raise NotImplementedError
