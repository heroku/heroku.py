from . import BaseResource, Plan


class Addon(BaseResource):
    """Heroku Addon."""

    _strs = ['id', 'config']
    _pks = ['id']
    _map = {'plan': Plan}
    _dates = ['created_at', 'updated_at']

    def __repr__(self):
        return "<addon '{0}'>".format(self.plan.name)

    def delete(self):
        """Uninstalls the addon"""
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.id, 'addons', self.id)
        )
        r.raise_for_status()
        return r.ok

    def upgrade(self, plan_id_or_name):

        """Upgrades an addon to the given plan."""

        payload = {'plan': plan_id_or_name}

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.id, 'addons', self.id),
            data=self._h._resource_serialize(payload)
        )

        print r.content.decode("utf-8")
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Addon.new_from_dict(item, h=self._h, app=self.app)
