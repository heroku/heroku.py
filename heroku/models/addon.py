from availableaddon import AvailableAddon
import sys

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote


class Addon(AvailableAddon):
    """Heroku Addon."""

    _pks = ['name', 'type']
    _strs = ['name', 'description', 'url', 'state', 'attachment_name']

    def __repr__(self):
        return "<addon '{0}'>".format(self.name)

    def delete(self):
        addon_name = self.name
        try:
            addon_name = self.attachment_name
        except:
            pass
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'addons', addon_name)
        )
        return r.ok

    def new(self, name, params=None):
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'addons', name),
            params=params
        )
        r.raise_for_status()
        return self.app.addons[name]

    def upgrade(self, name, params=None):
        """Upgrades an addon to the given tier."""
        # Allow non-namespaced upgrades. (e.g. advanced vs logging:advanced)
        if ':' not in name:
            name = '{0}:{1}'.format(self.type, name)

        r = self._h._http_resource(
            method='PUT',
            resource=('apps', self.app.name, 'addons', quote(name)),
            params=params,
            data=' '   # Server weirdness.
        )
        r.raise_for_status()
        return self.app.addons[name]


