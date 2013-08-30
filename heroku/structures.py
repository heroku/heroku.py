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
        self._kwargs = {}

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

    def __contains__(self, key):

        v = None
        try:
            v = self[key]
        except KeyError:
            return False
        else:
            if v is None:
                return False
            else:
                return True

    def add(self, *args, **kwargs):

        try:
            return self[0].new(*args, **kwargs)
        except IndexError:
            o = self._obj()
            o._h = self._h
            o.__dict__.update(self._kwargs)

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

    def append(self, items):
        self._items.append(items)


class DynoListResource(KeyedListResource):
    """KeyedListResource with basic filtering for process types."""

    def __init__(self, *args, **kwargs):
        super(DynoListResource, self).__init__(*args, **kwargs)

    def __getitem__(self, key):

        try:
            return super(DynoListResource, self).__getitem__(key)
        except KeyError as why:

            c = [p for p in self._items if key == p.type]

            if c:
                return DynoTypeListResource(items=c)
            else:
                raise why


class DynoTypeListResource(DynoListResource):
    """KeyedListResource with basic filtering for process types."""

    def __init__(self, *args, **kwargs):

        super(DynoTypeListResource, self).__init__(*args, **kwargs)


class SSHKeyListResource(KeyedListResource):
    """KeyedListResource with clearing for ssh keys."""

    def __init__(self, *args, **kwargs):

        super(SSHKeyListResource, self).__init__(*args, **kwargs)


class FilteredListResource(KeyedListResource):
    filter_func = staticmethod(lambda item: True)

    def __init__(self, items=None):
        items = [item for item in items if self.filter_func(item)] if items else []
        super(FilteredListResource, self).__init__(items)


def filtered_key_list_resource_factory(filter_func):
    return type('FilteredListResource', (FilteredListResource,), {'filter_func': staticmethod(filter_func)})
