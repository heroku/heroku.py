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

    def __contains__(self, key):
        v = None
        try:
            v = self[key]
        except KeyError:
            return False
        else:
            if v is None:
                return False
            else:
                return True

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        # API expects JSON.
        payload = json.dumps({key: value})

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=payload
        )

        self.data[key] = value
        return r.ok

    def __delitem__(self, key):
        data = self._h._resource_serialize({key: None})
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=data
        )

        del self.data[key]
        return r.ok

    def update(self, newconf):
        payload = self._h._resource_serialize(newconf)
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=payload
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return ConfigVars.new_from_dict(item, h=self)

    def to_dict(self):
        return self.data

    @classmethod
    def new_from_dict(cls, d, h=None, **kwargs):
        # Override normal operation because of crazy api.
        c = cls()
        c.data = d
        c._h = h
        c.app = kwargs.get('app')

        return c
