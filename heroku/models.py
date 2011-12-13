# -*- coding: utf-8 -*-

"""
heroku.models
~~~~~~~~~~~~~

This module contains the models that comprise the Heroku API.
"""

from .helpers import to_python, to_api

class BaseResource(object):

    _strs = []
    _ints = []
    _dates = []
    _bools = []
    _map = {}
    # _writeable = []
    # _cache = {}

    def __init__(self):
        self._bootstrap()
        super(BaseResource, self).__init__()

    def _bootstrap(self):
        """Bootstraps the model object based on configured values."""

        for attr in self._keys():
            setattr(self, attr, None)

    def _keys(self):
        return self._strs + self._ints + self._dates + self._bools + self._map.keys()

    def dict(self):
        d = dict()
        for k in self.keys():
            d[k] = self.__dict__.get(k)

        return d


    @classmethod
    def new_from_dict(cls, d, h=None):

        return to_python(
            obj=cls(), in_dict=d,
            str_keys = cls._strs,
            int_keys = cls._ints,
            date_keys = cls._dates,
            bool_keys = cls._bools,
            object_map = cls._map,
            _h = h
        )


class Addon(BaseResource):

    _strs = ['name', 'description', 'url', 'state']
    _bools = ['beta',]

    def __repr__(self):
        return "<addon '%s'>" % (self.name)

class App(BaseResource):
    _strs = ['name', 'create_status', 'stack', 'repo_migrate_status']
    _ints = ['id', 'slug_size', 'repo_size', 'dynos', 'workers']
    _dates = ['created_at',]

    def __init__(self):
        super(App, self).__init__()

    def __repr__(self):
        return "<app '%s'>" % (self.name)


class Collaborator(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Config(BaseResource):
    def __init__(self):
        super(App, self).__init__()

class Domain(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Key(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Log(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Process(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Release(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Stack(BaseResource):
    def __init__(self):
        super(App, self).__init__()


