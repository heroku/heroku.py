# -*- coding: utf-8 -*-

"""
heroku.models
~~~~~~~~~~~~~

This module contains the models that comprise the Heroku API.
"""

from ..helpers import to_python
#from .structures import DynoListResource#, filtered_key_list_resource_factory
#from .rendezvous import Rendezvous
from pprint import pprint # noqa
import sys

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote # noqa


class BaseResource(object):

    _strs = []
    _ints = []
    _dates = []
    _bools = []
    _dicts = []
    _map = {}
    _pks = []
    order_by = 'id'

    def __init__(self):
        self._bootstrap()
        self._h = None
        super(BaseResource, self).__init__()

    def __repr__(self):
        return "<resource '{0}'>".format(self._id)

    def _bootstrap(self):
        """Bootstraps the model object based on configured values."""

        for attr in self._keys():
            setattr(self, attr, None)

    def _keys(self):
        return self._strs + self._ints + self._dates + self._bools + list(self._map.keys())

    @property
    def _id(self):
        try:
            return getattr(self, self._pks[0])
        except IndexError:
            return None

    @property
    def _ids(self):
        """The list of primary keys to validate against."""
        for pk in self._pks:
            yield getattr(self, pk)

        for pk in self._pks:

            try:
                yield str(getattr(self, pk))
            except ValueError:
                pass

    def dict(self):
        d = dict()
        for k in self.keys():
            d[k] = self.__dict__.get(k)

        return d

    def change_connection(self, h):
        self._h = h
        return self

    @classmethod
    def new_from_dict(cls, d, h=None, **kwargs):

        d = to_python(
            obj=cls(),
            in_dict=d,
            str_keys=cls._strs,
            int_keys=cls._ints,
            date_keys=cls._dates,
            bool_keys=cls._bools,
            dict_keys=cls._dicts,
            object_map=cls._map,
            _h=h
        )

        d.__dict__.update(kwargs)

        return d


class Price(BaseResource):
    """Heroku Price."""

    _strs = ['cents', 'unit']
    _pks = ['cents']

    def __init__(self):
        self.app = None
        super(Price, self).__init__()

    def __repr__(self):
        return "<price '{0} per {1}'>".format(self.cents, self.unit)


class Plan(BaseResource):
    """Heroku Addon."""

    _strs = ['id', 'name', 'description', 'state']
    _pks = ['name', 'id']
    _map = {'price': Price}
    _dates = ['created_at', 'updated_at']

    def __repr__(self):
        return "<Plan '{0}'>".format(self.name)


class Stack(BaseResource):
    """Heroku Stack."""

    _strs = ['id', 'name']
    _pks = ['id', 'name']

    def __init__(self):
        self.app = None
        super(Stack, self).__init__()

    def __repr__(self):
        return "<stack '{0}'>".format(self.name)


class User(BaseResource):
    """Heroku User."""

    _strs = ['id', 'email']
    _pks = ['id', 'email']

    def __init__(self):
        self.app = None
        super(User, self).__init__()

    def __repr__(self):
        return "<user '{0}'>".format(self.email)


#class Plan(BaseResource):
    #"""Heroku Addon."""
#
    #_strs = ['id', 'name']
    #_pks = ['id', 'name']
#
    #def __init__(self):
        #self.app = None
        #super(Plan, self).__init__()

    #def __repr__(self):
        #return "<plan '{0} {1}'>".format(self.id, self.name)
#

class RateLimit(BaseResource):
    _strs = ['remaining']
    _bools = []
    _pks = ['remaining']

    def __init__(self):
        self.app = None
        super(RateLimit, self).__init__()

    def __repr__(self):
        return "<RateLimit '{0}'>".format(self.remaining)
