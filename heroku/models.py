# -*- coding: utf-8 -*-

"""
heroku.models
~~~~~~~~~~~~~

This module contains the models that comprise the Heroku API.
"""

from .helpers import to_python
from .structures import *
from urllib import quote
import json
import requests



class BaseResource(object):

    _strs = []
    _ints = []
    _dates = []
    _bools = []
    _dicts = []
    _map = {}
    _pks = []

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
        return self._strs + self._ints + self._dates + self._bools + self._map.keys()

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


class AvailableAddon(BaseResource):
    """Heroku Addon."""

    _strs = ['name', 'description', 'url', 'state']
    _bools = ['beta',]
    _pks = ['name']

    def __repr__(self):
        return "<available-addon '{0}'>".format(self.name)

    @property
    def type(self):
        return self.name.split(':')[0]


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


class App(BaseResource):
    """Heroku App."""

    _strs = ['name', 'create_status', 'stack', 'repo_migrate_status']
    _ints = ['id', 'slug_size', 'repo_size', 'dynos', 'workers']
    _dates = ['created_at',]
    _pks = ['name', 'id']

    def __init__(self):
        super(App, self).__init__()

    def __repr__(self):
        return "<app '{0}'>".format(self.name)

    def new(self, name=None, stack='cedar'):
        """Creates a new app."""

        payload = {}

        if name:
            payload['app[name]'] = name

        if stack:
            payload['app[stack]'] = stack

        r = self._h._http_resource(
            method='POST',
            resource=('apps',),
            data=payload
        )

        name = json.loads(r.content).get('name')
        return self._h.apps.get(name)

    @property
    def addons(self):
        return self._h._get_resources(
            resource=('apps', self.name, 'addons'),
            obj=Addon, app=self
        )

    @property
    def collaborators(self):
        """The collaborators for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'collaborators'),
            obj=Collaborator, app=self
        )

    @property
    def domains(self):
        """The domains for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'domains'),
            obj=Domain, app=self
        )

    @property
    def releases(self):
        """The releases for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'releases'),
            obj=Release, app=self
        )

    @property
    def processes(self):
        """The proccesses for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'ps'),
            obj=Process, app=self, map=ProcessListResource
        )

    @property
    def config(self):
        """The envs for this app."""

        return self._h._get_resource(
            resource=('apps', self.name, 'config_vars'),
            obj=ConfigVars, app=self
        )

    @property
    def info(self):
        """Returns current info for this app."""

        return self._h._get_resource(
            resource=('apps', self.name),
            obj=App,
        )

    @property
    def labs(self):
        return self._h._get_resources(
            resource=('features'),
            obj=Feature, params={'app': self.name}, app=self, map=filtered_key_list_resource_factory(lambda item: item.kind == 'app')
        )

    def rollback(self, release):
        """Rolls back the release to the given version."""
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'releases'),
            data={'rollback': release}
        )
        return self.releases[-1]


    def rename(self, name):
        """Renames app to given name."""

        r = self._h._http_resource(
            method='PUT',
            resource=('apps', self.name),
            data={'app[name]': name}
        )
        return r.ok

    def transfer(self, user):
        """Transfers app to given username's account."""

        r = self._h._http_resource(
            method='PUT',
            resource=('apps', self.name),
            data={'app[transfer_owner]': user}
        )
        return r.ok

    def maintenance(self, on=True):
        """Toggles maintenance mode."""

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'server', 'maintenance'),
            data={'maintenance_mode': int(on)}
        )
        return r.ok

    def destroy(self):
        """Destoys the app. Do be careful."""

        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.name)
        )
        return r.ok

    def logs(self, num=None, source=None, ps=None, tail=False):
        """Returns the requested log."""

        # Bootstrap payload package.
        payload = {'logplex': 'true'}

        if num:
            payload['num'] = num

        if source:
            payload['source'] = source

        if ps:
            payload['ps'] = ps

        if tail:
            payload['tail'] = 1

        # Grab the URL of the logplex endpoint.
        r = self._h._http_resource(
            method='GET',
            resource=('apps', self.name, 'logs'),
            data=payload
        )

        # Grab the actual logs.
        r = requests.get(r.content, verify=False, stream=True)

        if not tail:
            return r.content
        else:
            # Return line iterator for tail!
            return r.iter_lines()



class Collaborator(BaseResource):
    """Heroku Collaborator."""

    _strs = ['access', 'email']
    _pks = ['email']

    def __init__(self):
        self.app = None
        super(Collaborator, self).__init__()

    def __repr__(self):
        return "<collaborator '{0}'>".format(self.email)

    def new(self, email):
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'collaborators'),
            data={'collaborator[email]': email}
        )

        return self.app.collaborators[email]

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'collaborators', self.email)
        )

        return r.ok


class ConfigVars(object):
    """Heroku ConfigVars."""

    def __init__(self):

        self.data = {}
        self.app = None
        self._h = None

        super(ConfigVars, self).__init__()

    def __repr__(self):
        return repr(self.data)

    def __setitem__(self, key, value):
        # API expects JSON.
        payload = json.dumps({key: value})

        r = self._h._http_resource(
            method='PUT',
            resource=('apps', self.app.name, 'config_vars'),
            data=payload
        )

        return r.ok

    def __delitem__(self, key):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'config_vars', key),
        )

        return r.ok

    @classmethod
    def new_from_dict(cls, d, h=None, **kwargs):
        # Override normal operation because of crazy api.
        c = cls()
        c.data = d
        c._h = h
        c.app = kwargs.get('app')

        return c


class Domain(BaseResource):
    """Heroku Domain."""

    _ints = ['id', 'app_id', ]
    _strs = ['domain', 'base_domain', 'default']
    _dates = ['created_at', 'updated_at']
    _pks = ['domain', 'id']


    def __init__(self):
        self.app = None
        super(Domain, self).__init__()

    def __repr__(self):
        return "<domain '{0}'>".format(self.domain)

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'domains', self.domain)
        )

        return r.ok

    def new(self, name):
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'domains'),
            data={'domain_name[domain]': name}
        )

        return self.app.domains[name]


class Key(BaseResource):
    """Heroku SSH Key."""

    _strs = ['email', 'contents']
    _pks = ['id',]

    def __init__(self):
        super(Key, self).__init__()

    def __repr__(self):
        return "<key '{0}'>".format(self.id)

    @property
    def id(self):
        """Returns the username@hostname description field of the key."""

        return self.contents.split()[-1]

    def new(self, key):
        r = self._h._http_resource(
            method='POST',
            resource=('user', 'keys'),
            data=key
        )

        return self._h.keys.get(key.split()[-1])

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

    _strs = [
        'app_name', 'slug', 'command', 'upid', 'process', 'action',
        'rendezvous_url', 'pretty_state', 'state'
    ]

    _ints = ['elapsed']
    _bools = ['attached']
    _dates = []
    _pks = ['process', 'upid']


    def __init__(self):
        self.app = None
        super(Process, self).__init__()

    def __repr__(self):
        return "<process '{0}'>".format(self.process)

    def new(self, command, attach=""):
        """
        Creates a new Process
        Attach: If attach=True it will return a rendezvous connection point, for streaming stdout/stderr
        Command: The actual command it will run
        """
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps',),
            data={'attach': attach, 'command': command}
        )

        r.raise_for_status()
        return self.app.processes[r.json['process']]

    @property
    def type(self):
        return self.process.split('.')[0]

    def restart(self, all=False):
        """Restarts the given process."""

        if all:
            data = {'type': self.type}

        else:
            data = {'ps': self.process}

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps', 'restart'),
            data=data
        )

        r.raise_for_status()

    def stop(self, all=False):
        """Stops the given process."""

        if all:
            data = {'type': self.type}

        else:
            data = {'ps': self.process}

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps', 'stop'),
            data=data
        )

        r.raise_for_status()

    def scale(self, quantity):
        """Scales the given process to the given number of dynos."""

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps', 'scale'),
            data={'type': self.type, 'qty': quantity}
        )

        r.raise_for_status()

        if self.type in self.app.processes:
            return self.app.processes[self.type]
        else:
            return ProcessListResource()



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



class Stack(BaseResource):
    def __init__(self):
        super(Stack, self).__init__()


class Feature(BaseResource):
    _strs = ['name', 'kind', 'summary', 'docs',]
    _bools = ['enabled']
    _pks = ['name']

    def __init__(self):
        self.app = None
        super(Feature, self).__init__()

    def __repr__(self):
        return "<feature '{0}'>".format(self.name)

    def enable(self):
        r = self._h._http_resource(
            method='POST',
            resource=('features', self.name),
            params={'app': self.app.name if self.app else ''}
        )
        return r.ok

    def disable(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('features', self.name),
            params={'app': self.app.name if self.app else ''}
        )
        return r.ok
