from .  import BaseResource


class Region(BaseResource):
    _strs = ['description', 'id', 'name']
    _dates = ['created_at', 'updated_at']
    _pks = ['id', 'name']
    order_by = 'id'

    def __init__(self):
        self.app = None
        super(Region, self).__init__()

    def __repr__(self):
        return "<region '{0} {1}'>\n".format(self.name, self.id)
