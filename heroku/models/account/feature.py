from .. import BaseResource


class AccountFeature(BaseResource):
    _strs = ['name', 'description', 'doc_url', 'id']
    _bools = ['enabled']
    _dates = ['created_at', 'updated_at']
    _pks = ['id', 'name']

    def __init__(self):
        self.app = None
        super(AccountFeature, self).__init__()

    def __repr__(self):
        return "<account_feature '{0}'>".format(self.name)

    def update(self, enabled):
        r = self._h._http_resource(
            method='POST',
            resource=('account', 'features', self.id),
            data=self._h._resource_serialize({'enabled': enabled})
        )
        r.raise_for_status()
        return r.ok

    def enable(self):
        return self.update(True)

    def disable(self):
        return self.update(0)
