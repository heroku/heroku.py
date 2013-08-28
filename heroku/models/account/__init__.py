from ...models import BaseResource
from ..key import Key
from .feature import AccountFeature
import sys

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote # noqa


class Account(BaseResource):

    _strs = ['email', 'id']
    _bools = ['allow_tracking', 'beta', 'verified']
    _pks = ['id']
    _dates = ['created_at', 'last_login', 'updated_at']

    def __repr__(self):
        return "<account '{0}'>".format(self.email)

    def keys(self, **kwargs):
        """The collaborators for this app."""
        return self._h._get_resources(
            resource=('account', 'keys'),
            obj=Key, app=self, **kwargs
        )

    def add_key(self, key):
        r = self._h._http_resource(
            method='POST',
            resource=('account', 'keys'),
            data=self._h._resource_serialize({'public_key': key})
        )
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Key.new_from_dict(item, h=self._h)

    def remove_key(self, key_or_fingerprint):
        """Deletes the key."""
        r = self._h._http_resource(
            method='DELETE',
            resource=('account', 'keys', quote(key_or_fingerprint))
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Key.new_from_dict(item, h=self._h)

    def disable_feature(self, id_or_name):
        return self.update_feature(id_or_name, 0)

    def enable_feature(self, id_or_name):
        return self.update_feature(id_or_name, True)

    def update_feature(self, id_or_name, enabled):

        payload = {'enabled': enabled}
        r = self._h._http_resource(
            method='PATCH',
            resource=('account', 'features', id_or_name),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AccountFeature.new_from_dict(item, h=self._h, app=self)

    def change_password(self, current_password, new_password):
        r = self._h._http_resource(
            method='PUT',
            resource=('account', 'password'),
            data=self._h._resource_serialize({'current_password': current_password, 'new_password': new_password})
        )
        r.raise_for_status()
        return r.ok
