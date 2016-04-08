from baseresource import BaseResource


class Log(BaseResource):
    def __init__(self):
        self.app = None
        super(Log, self).__init__()
