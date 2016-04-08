from baseresource import BaseResource


class Domain(BaseResource):
    """Heroku Domain."""

    _ints = ['id', 'app_id', ]
    _strs = ['domain', 'base_domain', 'default']
    _dates = ['created_at', 'updated_at']
    _pks = ['domain', 'id']

    def __init__(self):
        self.app = None
        super(Domain, self).__init__()

    def __repr__(self):
        return "<domain '{0}'>".format(self.domain)

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'domains', self.domain)
        )

        return r.ok

    def new(self, name):
        self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'domains'),
            data={'domain_name[domain]': name}
        )

        return self.app.domains[name]


