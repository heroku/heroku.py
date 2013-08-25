from .  import BaseResource, User


class Collaborator(BaseResource):
    """Heroku Collaborator."""

    _bools = ['silent']
    _dates = ['created_at', 'updated_at']
    _strs = ['id']
    _pks = ['id']
    _map = {'user': User}

    def __init__(self):
        self.app = None
        super(Collaborator, self).__init__()

    def __repr__(self):
        return "<collaborator '{0}'>".format(self.user.email)

    def remove(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'collaborators', self.user.email)
        )
        r.raise_for_status()

        return r.ok
