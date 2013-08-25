from .  import BaseResource


class Key(BaseResource):
    """Heroku SSH Key."""

    _strs = ['id', 'public_key', 'email', 'fingerprint']
    _dates = ['created_at', 'updated_at']
    _pks = ['id']

    def __init__(self):
        super(Key, self).__init__()

    def __repr__(self):
        return "<key '{0}-{1}'>".format(self.id, self.email)

    def delete(self):
        """Deletes the key."""
        r = self._h._http_resource(
            method='DELETE',
            resource=('account', 'keys', self.id)
        )

        r.raise_for_status()
        return self
