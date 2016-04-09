from baseresource import BaseResource


class Key(BaseResource):
    """Heroku SSH Key."""

    _strs = ['email', 'contents']
    _pks = ['id']

    def __init__(self):
        super(Key, self).__init__()

    def __repr__(self):
        return "<key '{0}'>".format(self.id)

    @property
    def id(self):
        """Returns the username@hostname description field of the key."""

        return self.contents.split()[-1]

    def new(self, key):
        self._h._http_resource(
            method='POST',
            resource=('user', 'keys'),
            data=key
        )

        return self._h.keys.get(key.split()[-1])

    def delete(self):
        """Deletes the key."""
        r = self._h._http_resource(
            method='DELETE',
            resource=('user', 'keys', self.id)
        )

        r.raise_for_status()


