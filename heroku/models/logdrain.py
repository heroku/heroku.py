from .  import BaseResource
from .addon import Addon


class LogDrain(BaseResource):
    _strs = ['id', 'url']
    _map = {'addon': Addon}
    _dates = ['created_at', 'updated_at']
    _pks = ['id']

    def __init__(self):
        self.app = None
        super(LogDrain, self).__init__()

    def __repr__(self):
        return "<logdrain '{0}'>".format(self.id)

    def remove(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.id, 'log-drains', self.id)
        )

        r.raise_for_status()

        return r.ok
