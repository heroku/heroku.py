# -*- coding: utf-8 -*-

"""
heroku.structures
~~~~~~~~~~~~~~~~~

This module contains the specific Heroku.py data types.
"""


class KeyedListResource(object):
    """docstring for ListResource"""

    def __init__(self, items=None):
        super(KeyedListResource, self).__init__()

        self._h = None
        self._items = items or list()
        self._obj = None

    def __repr__(self):
        return repr(self._items)

    def __iter__(self):
        for item in self._items:
            yield item

    def __getitem__(self, key):

        # Support index operators.
        if isinstance(key, int):
            if abs(key) <= len(self._items):
                return self._items[key]

        v = self.get(key)

        if v is None:
            raise KeyError(key)

        return v

    def add(self, *args, **kwargs):

        try:
            return self[0].new(*args, **kwargs)
        except IndexError:
            o = self._obj()
            o._h = self._h

            return o.new(*args, **kwargs)


    def remove(self, key):
        if hasattr(self[0], 'delete'):
            return self[key].delete()

    def get(self, key):
        for item in self:
            if key in item._ids:
                return item

    def __delitem__(self, key):
        self[key].delete()



class ProcessListResource(KeyedListResource):
    """KeyedListResource with basic filtering for process types."""

    def __init__(self, *args, **kwargs):
        super(ProcessListResource, self).__init__(*args, **kwargs)

    def __getitem__(self, key):

        try:
            return super(ProcessListResource, self).__getitem__(key)
        except KeyError, why:

            c = [p for p in self._items if key == p.type]

            if c:
                return ProcessTypeListResource(items=c)
            else:
                raise why


class ProcessTypeListResource(ProcessListResource):
    """KeyedListResource with basic filtering for process types."""

    def __init__(self, *args, **kwargs):

        super(ProcessTypeListResource, self).__init__(*args, **kwargs)

    def scale(self, quantity):
        return self[0].scale(quantity)



class SSHKeyListResource(KeyedListResource):
    """KeyedListResource with clearing for ssh keys."""

    def __init__(self, *args, **kwargs):

        super(SSHKeyListResource, self).__init__(*args, **kwargs)

    def clear(self):
        """Removes all SSH keys from a user's system."""

        r = self._h._http_resource(
            method='DELETE',
            resource=('user', 'keys'),
        )

        return r.ok




