class StorageDriver(object):
    """
    Abstract class for storage interfaces
    """
    def __init__(self):
        pass

    def add_token(self, **kwargs):
        raise NotImplementedError

    def add_event(self, **kwargs):
        raise NotImplementedError

    def delete(self, **kwargs):
        raise NotImplementedError

    def get_token(self, **kwargs):
        raise NotImplementedError

    def get_event(self, **kwargs):
        raise NotImplementedError

    def update(self, **kwargs):
        raise NotImplementedError
