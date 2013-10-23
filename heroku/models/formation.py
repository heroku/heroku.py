from .  import BaseResource
import sys


if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote # noqa


class Formation(BaseResource):

    _strs = ['id', 'command', 'type', 'size']
    _ints = ['quantity']
    _bools = ['attached']
    _dates = ['created_at', 'updated_at']
    _pks = ['id', 'type']

    def __init__(self):
        self.app = None
        super(Formation, self).__init__()

    def __repr__(self):
        return "<formation '{0} - {1}'>".format(self.type, self.command)

    def scale(self, quantity):
        """Scales the given process to the given number of dynos."""
        return self.update(quantity=quantity)

    def resize(self, size):
        """Resizes the Dynos to the multiple given"""
        return self.update(size=size)

    def update(self, size=None, quantity=None):

        assert(size or quantity == 0 or quantity)
        payload = {}
        if size:
            payload['size'] = size

        if quantity or quantity == 0:
            payload['quantity'] = quantity

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.id, 'formation', quote(self.type)),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        return self._h._process_item(self._h._resource_deserialize(r.content.decode("utf-8")), Formation)
