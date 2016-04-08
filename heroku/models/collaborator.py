from baseresource import BaseResource


class Collaborator(BaseResource):
    """Heroku Collaborator."""

    _strs = ['access', 'email']
    _pks = ['email']

    def __init__(self):
        self.app = None
        super(Collaborator, self).__init__()

    def __repr__(self):
        return "<collaborator '{0}'>".format(self.email)

    def new(self, email):
        self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'collaborators'),
            data={'collaborator[email]': email}
        )

        return self.app.collaborators[email]

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'collaborators', self.email)
        )

        return r.ok


