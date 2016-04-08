from baseresource import BaseResource


class AvailableAddon(BaseResource):
    """Heroku Addon."""

    _strs = ['name', 'description', 'url', 'state']
    _bools = ['beta']
    _pks = ['name']

    def __repr__(self):
        return "<available-addon '{0}'>".format(self.name)

    @property
    def type(self):
        return self.name.split(':')[0]
