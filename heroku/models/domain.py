from . import BaseResource


class Domain(BaseResource):
    """Heroku Domain."""

    _strs = ['id', 'hostname']
    _dates = ['created_at', 'updated_at']
    _pks = ['hostname', 'id']
    order_by = 'domain'

    def __init__(self):
        self.app = None
        super(Domain, self).__init__()

    def __repr__(self):
        return "<domain '{0}'>".format(self.hostname)

    def remove(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'domains', self.hostname)
        )

        r.raise_for_status()

        return r.ok
