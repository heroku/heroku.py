from baseresource import BaseResource


class Release(BaseResource):
    _strs = ['name', 'descr', 'user', 'commit', 'addons']
    _dicts = ['env', 'pstable']
    _dates = ['created_at']
    _pks = ['name']

    def __init__(self):
        self.app = None
        super(Release, self).__init__()

    def __repr__(self):
        return "<release '{0}'>".format(self.name)

    def rollback(self):
        """Rolls back the application to this release."""

        return self.app.rollback(self.name)
