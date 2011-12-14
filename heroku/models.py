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
    _dicts = []
    _map = {}
    # _writeable = []
    # _cache = {}

    def __init__(self):
        self._bootstrap()
        self._h = None
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
    def new_from_dict(cls, d, h=None, **kwargs):

        d = to_python(
            obj=cls(),
            in_dict=d,
            str_keys=cls._strs,
            int_keys=cls._ints,
            date_keys=cls._dates,
            bool_keys=cls._bools,
            dict_keys= cls._dicts,
            object_map=cls._map,
            _h = h
        )

        d.__dict__.update(kwargs)

        return d


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

    def collaborators(self):
        return self._h._get_resources(
            resource=('apps', self.name, 'collaborators'),
            obj=Collaborator, app=self
        )

    def domains(self):
        return self._h._get_resources(
            resource=('apps', self.name, 'domains'),
            obj=Domain, app=self
        )

    def releases(self):
        return self._h._get_resources(
            resource=('apps', self.name, 'releases'),
            obj=Release, app=self
        )

    def rollback(self, release):
        """Rolls back the release to the given version."""
        pass


class Collaborator(BaseResource):
    _strs = ['access', 'email']

    def __init__(self):
        self.app = None
        super(Collaborator, self).__init__()

    def __repr__(self):
        return "<collaborator '%s'>" % (self.email)


# class ConfigVars(BaseResource):
#     def __init__(self):
#         super(ConfigVars, self).__init__()


class Domain(BaseResource):
    _ints = ['id', 'app_id', ]
    _strs = ['domain', 'base_domain', 'default']
    _dates = ['created_at', 'updated_at']


    def __init__(self):
        self.app = None
        super(Domain, self).__init__()

    def __repr__(self):
        return "<domain '%s'>" % (self.domain)


class Key(BaseResource):
    _strs = ['email', 'contents']

    def __init__(self):
        super(Key, self).__init__()

    def __repr__(self):
        return "<key '%s'>" % (self.id)

    @property
    def id(self):
        """Returns the username@hostname description field of the key."""

        return self.contents.split()[-1]


    def delete(self):
        """Deletes the key."""
        r = self._h._http_resource(
            method='DELETE',
            resource=('user', 'keys', self.id)
        )

        r.raise_for_status()


class Log(BaseResource):
    def __init__(self):
        self.app = None
        super(Log, self).__init__()


class Process(BaseResource):
    def __init__(self):
        self.app = None
        super(Process, self).__init__()


class Release(BaseResource):
    _strs = ['name', 'descr', 'user', 'commit', 'addons']
    _dicts = ['env', 'pstable']
    _dates = ['created_at']

    def __init__(self):
        self.app = None
        super(Release, self).__init__()

    def __repr__(self):
        return "<release '%s'>" % (self.name)

    def rollback(self):
        """Rolls back the application to this release."""

        assert self.app

        return self.app.rollback(self.name)



class Stack(BaseResource):
    def __init__(self):
        super(Stack, self).__init__()


