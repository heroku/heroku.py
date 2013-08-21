# -*- coding: utf-8 -*-

"""
heroku.models
~~~~~~~~~~~~~

This module contains the models that comprise the Heroku API.
"""

from .helpers import to_python
from .structures import *
import json
from pprint import pprint
import requests
import sys

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote


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

    @classmethod
    def new_for_create(cls, h=None, **kwargs):
        d = to_python(
            obj=cls(),
            in_dict={},
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

class User(BaseResource):
    """Heroku User."""

    _strs = ['id', 'email']
    _pks = ['id', 'email']

    def __init__(self):
        self.app = None
        super(User, self).__init__()

    def __repr__(self):
        return "<user '{0}'>".format(self.email)


class Plan(BaseResource):
    """Heroku Addon."""

    _strs = ['id', 'name']
    _pks = ['id', 'name']

    def __init__(self):
        self.app = None
        super(Plan, self).__init__()

    def __repr__(self):
        return "<plan '{0} {1}'>".format(self.id, self.name)


class Account(BaseResource):

    _strs = ['email', 'id']
    _bools = ['allow_tracking', 'beta', 'verified']
    _pks = ['id']
    _dates = ['created_at', 'last_login', 'updated_at']

    def __repr__(self):
        return "<account '{0}'>".format(self.email)


class AvailableAddon(BaseResource):
    """Heroku Addon."""

    _strs = ['id', 'name']
    _pks = ['id']
    _dates = ['created_at', 'updated_at']

    def __repr__(self):
        return "<available-addon '{0}'>".format(self.name)

    @property
    def type(self):
        return self.name.split(':')[0]


class Addon(AvailableAddon):
    """Heroku Addon."""

    _strs = ['id', 'config']
    _pks = ['id']
    _map = {'plan': Plan}
    _dates = ['created_at', 'updated_at']

    def __repr__(self):
        return "<addon '{0}'>".format(self.plan.name)

    def delete(self):
        """Uninstalls the addon"""
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.id, 'addons', self.id)
        )
        r.raise_for_status()
        return r.ok

    def upgrade(self, name=None, config=None):

        """Upgrades an addon to the given tier."""
        # Allow non-namespaced upgrades. (e.g. advanced vs logging:advanced)
        if ':' not in name:
            name = '{0}:{1}'.format(self.type, name)

        payload = {}
        plan = {}
        if not config:
            config = {}
        print "name = {0}".format(name)
        print "id = {0}".format(self.id)
        print "planid = {0}".format(self.plan.id)
        assert(name)
        plan['id'] = self.plan.id
        plan['name'] = name
        payload['config'] = config
        payload['plan'] = plan

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.id, 'addons', self.id),
            data=self._h._resource_serialize(payload)
        )

        print r.content.decode("utf-8")
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Addon.new_from_dict(item, h=self._h)


class App(BaseResource):
    """Heroku App."""

    _strs = ['buildpack_provided_description', 'git_url', 'id', 'name', 'owner:email', 'owner:id', 'region:id', 'region:name', 'stack', 'web_url']
    _ints = ['slug_size', 'repo_size']
    _bools = ['maintenance']
    _dates = ['archived_at', 'created_at', 'released_at', 'updated_at']
    _pks = ['name', 'id']

    def __init__(self):
        super(App, self).__init__()

    def __repr__(self):
        return "<app '{0}'>".format(self.name)

    @property
    def addons(self):
        return self._h._get_resources(
            resource=('apps', self.name, 'addons'),
            obj=Addon, app=self
        )

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id)
        )
        r.raise_for_status()
        return r.ok

    def add_collaborator(self, email=None, id=None, silent=False):

        assert(email or id)
        payload = {}
        user = {}
        if email:
            user['email'] = email
        if id:
            user['id'] = id

        if silent:
            silent = True

        #payload['silent'] = silent
        payload['user'] = user

        pprint(payload)

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'collaborators'),
            data=self._h._resource_serialize(payload)
        )

        print r.content.decode("utf-8")
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Collaborator.new_from_dict(item, h=self._h, app=self)

    def remove_collaborator(self, id_or_email):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.name, 'collaborators', id_or_email)
        )
        r.raise_for_status()

        return r.ok

    def install_addon(self, plan_id=None, plan_name=None, config=None):

        payload = {}
        plan = {}
        if not config:
            config = {}
        print "plan_id = {0}".format(plan_id)
        print "plan_name = {0}".format(plan_name)
        assert(plan_id or plan_name)
        if plan_id:
            plan['id'] = plan_id

        if plan_name:
            plan['name'] = plan_name

        payload['config'] = config
        payload['plan'] = plan

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'addons'),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Addon.new_from_dict(item, h=self._h, app=self)

    def collaborators(self):
        """The collaborators for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'collaborators'),
            obj=Collaborator, app=self
        )

    def config(self):
        """The envs for this app."""

        return self._h._get_resource(
            resource=('apps', self.name, 'config-vars'),
            obj=ConfigVars, app=self
        )

    def domains(self):
        """The domains for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'domains'),
            obj=Domain, app=self
        )

    def add_domain(self, hostname):

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'domains'),
            data=self._h._resource_serialize({'hostname': hostname})
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Domain.new_from_dict(item, h=self._h, app=self)

    def remove_domain(self, hostname):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.name, 'domains', hostname)
        )

        r.raise_for_status()

        return r.ok

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
        r = requests.get(r.content.decode("utf-8"), verify=False, stream=True)

        if not tail:
            return r.content
        else:
            # Return line iterator for tail!
            return r.iter_lines()


class Collaborator(BaseResource):
    """Heroku Collaborator."""

    _bools = ['silent']
    _dates = ['created_at', 'updated_at']
    _strs = ['id']
    _pks = ['id']
    _map = {'user': User}

    def __init__(self):
        self.app = None
        super(Collaborator, self).__init__()

    def __repr__(self):
        return "<collaborator '{0}'>".format(self.user.email)

    def remove(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'collaborators', self.user.email)
        )
        r.raise_for_status()

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
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=payload
        )

        return r.ok

    def __delitem__(self, key):
        data = self._h._resource_serialize({key: None})
        print data
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.name, 'config-vars'),
            data=data
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

    _strs = ['id', 'hostname']
    _dates = ['created_at', 'updated_at']
    _pks = ['hostname', 'id']

    def __init__(self):
        self.app = None
        super(Domain, self).__init__()

    def __repr__(self):
        return "<domain '{0}'>".format(self.hostname)

    def remove(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.name, 'domains', self.hostname)
        )

        r.raise_for_status()

        return r.ok


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
    _strs = ['description', 'id', 'user', 'commit', 'addons']
    #_dicts = ['env', 'pstable']
    _ints = ['version']
    _dates = ['created_at', 'updated_at']
    _map = {'user': User}
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
    _strs = ['name', 'kind', 'summary', 'docs']
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


class RateLimit(BaseResource):
    _strs = ['remaining']
    _bools = []
    _pks = ['remaining']

    def __init__(self):
        self.app = None
        super(RateLimit, self).__init__()

    def __repr__(self):
        return "<RateLimit '{0}'>".format(self.remaining)


class Dyno(BaseResource):
    _strs = ['id', 'attach_url', 'command', 'name', 'state', 'type']
    _bools = ['attach']
    _ints = ['size', 'repo_size']
    _dates = ['created_at', 'updated_at']
    _map = {'release': Release}
    _pks = ['id']

    def __init__(self):
        self.app = None
        super(Dyno, self).__init__()

    def __repr__(self):
        return "<Dyno '{0} - {1}'>".format(self.name, self.command)
