import json


class ConfigVars(object):
    """Heroku ConfigVars."""

    def __init__(self):

        self.data = {}
        self.app = None
        self._h = None

        super(ConfigVars, self).__init__()

    def __repr__(self):
        return repr(self.data)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        # API expects JSON.
        payload = json.dumps({key: value})

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=payload
        )

        return r.ok

    def __delitem__(self, key):
        data = self._h._resource_serialize({key: None})
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=data
        )

        return r.ok

    @classmethod
    def new_from_dict(cls, d, h=None, **kwargs):
        # Override normal operation because of crazy api.
        c = cls()
        c.data = d
        c._h = h
        c.app = kwargs.get('app')

        return c
