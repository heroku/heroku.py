from .  import BaseResource
import requests


class LogSession(BaseResource):
    _strs = ['id', 'logplex_url', 'dyno', 'source']
    _ints = ['lines']
    _bools = ['tail']
    _dates = ['created_at', 'updated_at']
    _pks = ['id']

    def __init__(self):
        self.app = None
        super(LogSession, self).__init__()

    def __repr__(self):
        return "<logsession '{0}'>".format(self.id)

    def stream(self, timeout=False):
        r = requests.get(self.logplex_url, verify=False, stream=True, timeout=timeout)
        return r.iter_lines()

    def get(self, timeout=False):
        r = requests.get(self.logplex_url, verify=False, stream=True, timeout=timeout)
        return r.content.decode("utf-8")
