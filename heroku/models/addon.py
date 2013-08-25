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

    def upgrade(self, name=None, config=None):

        """Upgrades an addon to the given tier."""
        # Allow non-namespaced upgrades. (e.g. advanced vs logging:advanced)
        if ':' not in name:
            name = '{0}:{1}'.format(self.type, name)

        payload = {}
        plan = {}
        if not config:
            config = {}
        print "name = {0}".format(name)
        print "id = {0}".format(self.id)
        print "planid = {0}".format(self.plan.id)
        assert(name)
        plan['id'] = self.plan.id
        plan['name'] = name
        payload['config'] = config
        payload['plan'] = plan

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.id, 'addons', self.id),
            data=self._h._resource_serialize(payload)
        )

        print r.content.decode("utf-8")
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Addon.new_from_dict(item, h=self._h, app=self.app)
