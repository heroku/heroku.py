from baseresource import BaseResource


class Feature(BaseResource):
    _strs = ['name', 'kind', 'summary', 'docs']
    _bools = ['enabled']
    _pks = ['name']

    def __init__(self):
        self.app = None
        super(Feature, self).__init__()

    def __repr__(self):
        return "<feature '{0}'>".format(self.name)

    def enable(self):
        r = self._h._http_resource(
            method='POST',
            resource=('features', self.name),
            params={'app': self.app.name if self.app else ''}
        )
        return r.ok

    def disable(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('features', self.name),
            params={'app': self.app.name if self.app else ''}
        )
        return r.ok
