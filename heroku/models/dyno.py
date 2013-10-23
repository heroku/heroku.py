from . import BaseResource
from .release import Release


class RestartRunException(Exception):
    pass


class Dyno(BaseResource):
    _strs = ['id', 'attach_url', 'size', 'command', 'name', 'state', 'type']
    _bools = ['attach']
    _ints = ['repo_size']
    _dates = ['created_at', 'updated_at']
    _map = {'release': Release}
    _pks = ['id']

    def __init__(self):
        self.app = None
        super(Dyno, self).__init__()

    def __repr__(self):
        return "<Dyno '{0} - {1}'>".format(self.name, self.command)

    def kill(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.id, 'dynos', self.id)
        )

        r.raise_for_status()

        return r.ok

    def restart(self):
        if self.type == 'run':
            raise RestartRunException("Unable to restart a Process of type 'run' as it will not be respawned by Heroku")
        else:
            return self.kill()
