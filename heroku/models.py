# -*- coding: utf-8 -*-

"""
heroku.models
~~~~~~~~~~~~~

This module contains the models that comprise the Heroku API.
"""

from .helpers import to_python
from .structures import DynoListResource#, filtered_key_list_resource_factory
from .rendezvous import Rendezvous
import json
from pprint import pprint
import requests
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

    def add_key(self, key):
        r = self._h._http_resource(
            method='POST',
            resource=('account', 'keys'),
            data=self._h._resource_serialize({'public_key': key})
        )
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Key.new_from_dict(item, h=self._h)

    def remove_key(self, key_or_fingerprint):
        """Deletes the key."""
        r = self._h._http_resource(
            method='DELETE',
            resource=('account', 'keys', quote(key_or_fingerprint))
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Key.new_from_dict(item, h=self._h)

    def disable_feature(self, id_or_name):
        return self.update_feature(id_or_name, 0)

    def enable_feature(self, id_or_name):
        return self.update_feature(id_or_name, True)

    def update_feature(self, id_or_name, enabled):

        payload = {'enabled': enabled}
        print payload
        r = self._h._http_resource(
            method='PATCH',
            resource=('account', 'features', id_or_name),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AccountFeature.new_from_dict(item, h=self._h, app=self)


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
        return Addon.new_from_dict(item, h=self._h, app=self.app)


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

    def addons(self, **kwargs):
        return self._h._get_resources(
            resource=('apps', self.name, 'addons'),
            obj=Addon, app=self, **kwargs
        )

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id)
        )
        r.raise_for_status()
        return r.ok

    def add_collaborator(self, email=None, id=None, silent=0):

        assert(email or id)
        payload = {}
        user = {}
        if email:
            user['email'] = email
        if id:
            user['id'] = id

        if silent:
            silent = True

        payload['silent'] = silent
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

    def collaborators(self, **kwargs):
        """The collaborators for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'collaborators'),
            obj=Collaborator, app=self, **kwargs
        )

    def config(self):
        """The envs for this app."""

        return self._h._get_resource(
            resource=('apps', self.name, 'config-vars'),
            obj=ConfigVars, app=self
        )

    def domains(self, **kwargs):
        """The domains for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'domains'),
            obj=Domain, app=self, **kwargs
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

    def dynos(self, **kwargs):
        """The proccesses for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'dynos'),
            obj=Dyno, app=self, map=DynoListResource, **kwargs
        )

    def remove_dyno(self, dyno_id_or_name):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id, 'dynos', quote(dyno_id_or_name))
        )

        r.raise_for_status()

        return r.ok

    def restart(self):
        for formation in self.process_formation():
            formation.restart()
        return self

    def run_command_detached(self, command, printout=True, size=1):
        """Run a remote command but do not wait for the command to complete"""
        return self.run_command(command, attach=False, printout=printout, size=size)

    def run_command(self, command, attach=True, printout=True, size=1):
        """Run a remote command attach=True if you want to capture the output"""
        if attach:
            attach = True
        payload = {'command': command, 'attach': attach, 'size': size}

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'dynos'),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        dyno = Dyno.new_from_dict(item, h=self._h, app=self)

        if attach:
            output = Rendezvous(dyno.attach_url, printout).start()
            return output, dyno
        else:
            return dyno

    def process_formation(self, **kwargs):
        """The formation processes for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'formation'),
            obj=Formation, app=self, **kwargs#, map=DynoListResource
        )

    def releases(self, **kwargs):
        """The releases for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'releases'),
            obj=Release, app=self, **kwargs
        )

    @property
    def info(self):
        """Returns current info for this app."""

        return self._h._get_resource(
            resource=('apps', self.name),
            obj=App,
        )

    def labs(self, **kwargs):
        return self.features(**kwargs)

    def features(self, **kwargs):
        return self._h._get_resources(
            resource=('apps', self.id, 'features'),
            obj=AppFeature, app=self, **kwargs
        )

    def disable_feature(self, id_or_name):
        return self.update_feature(id_or_name, 0)

    def enable_feature(self, id_or_name):
        return self.update_feature(id_or_name, True)

    def update_feature(self, id_or_name, enabled):

        payload = {'enabled': enabled}
        print payload
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.id, 'features', id_or_name),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AppFeature.new_from_dict(item, h=self._h, app=self)

    def rollback(self, release):
        """Rolls back the release to the given version."""
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'releases'),
            data={'rollback': release}
        )
        r.raise_for_status()
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
    order_by = 'domain'

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

    _strs = ['id', 'publis_key', 'email', 'fingerprint']
    _dates = ['created_at', 'updated_at']
    _pks = ['id']

    def __init__(self):
        super(Key, self).__init__()

    def __repr__(self):
        return "<key '{0}-{1}'>".format(self.id, self.email)

    def delete(self):
        """Deletes the key."""
        r = self._h._http_resource(
            method='DELETE',
            resource=('account', 'keys', self.id)
        )

        r.raise_for_status()
        return self


class Log(BaseResource):
    def __init__(self):
        self.app = None
        super(Log, self).__init__()


class Formation(BaseResource):

    _strs = ['id', 'command', 'type']
    _ints = ['quantity', 'size']
    _bools = ['attached']
    _dates = ['created_at', 'updated_at']
    _pks = ['process', 'upid']

    def __init__(self):
        self.app = None
        super(Formation, self).__init__()

    def __repr__(self):
        return "<formation '{0}-{1}'>".format(self.type, self.command)

    def restart(self):
        """Restarts the given process."""

        data = {'type': self.type}

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps', 'restart'),
            data=data,
            legacy=True
        )

        r.raise_for_status()

    def scale(self, quantity):
        """Scales the given process to the given number of dynos."""
        if quantity > 0:
            return self.update(quantity=quantity)
        return self.update(quantity=quantity)

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps', 'scale'),
            data={'type': self.type, 'qty': quantity},
            legacy=True
        )

        r.raise_for_status()

        return self

    def size(self, size):
        return self.update(size=size)

    def update(self, size=None, quantity=None):
        print "size = {0}".format(size)
        print "quantity = {0}".format(quantity)

        assert(size or quantity == 0 or quantity)
        payload = {}
        if size:
            payload['size'] = size

        if quantity:
            payload['quantity'] = quantity

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.app.id, 'formation', quote(self.type)),
            data=self._h._resource_serialize(payload)
        )

        print r.content.decode("utf-8")
        r.raise_for_status()
        return self._h._process_items(self._h._resource_deserialize(r.content.decode("utf-8")), Formation)


class Release(BaseResource):
    _strs = ['description', 'id', 'user', 'commit', 'addons']
    #_dicts = ['env', 'pstable']
    _ints = ['version']
    _dates = ['created_at', 'updated_at']
    _map = {'user': User}
    _pks = ['id', 'version']
    order_by = 'seq'

    def __init__(self):
        self.app = None
        super(Release, self).__init__()

    def __repr__(self):
        return "<release '{0} {1} {2}'>\n".format(self.version, self.created_at, self.description)

    #def rollback(self):
        #"""Rolls back the application to this release."""
        #return self.app.rollback(self.name)


class Stack(BaseResource):
    def __init__(self):
        super(Stack, self).__init__()


class AppFeature(BaseResource):
    _strs = ['name', 'description', 'doc_url', 'id']
    _bools = ['enabled']
    _dates = ['created_at', 'updated_at']
    _pks = ['id', 'name']

    def __init__(self):
        self.app = None
        super(AppFeature, self).__init__()

    def __repr__(self):
        return "<app_feature '{0}'>".format(self.name)

    def update(self, enabled):
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.id, 'features', self.id),
            data=self._h._resource_serialize({'enabled': enabled})
        )
        r.raise_for_status()
        return r.ok

    def enable(self):
        return self.update(True)

    def disable(self):
        return self.update(0)


class AccountFeature(BaseResource):
    _strs = ['name', 'description', 'doc_url', 'id']
    _bools = ['enabled']
    _dates = ['created_at', 'updated_at']
    _pks = ['id', 'name']

    def __init__(self):
        self.app = None
        super(AccountFeature, self).__init__()

    def __repr__(self):
        return "<account_feature '{0}'>".format(self.name)

    def update(self, enabled):
        r = self._h._http_resource(
            method='POST',
            resource=('account', 'features', self.id),
            data=self._h._resource_serialize({'enabled': enabled})
        )
        r.raise_for_status()
        return r.ok

    def enable(self):
        return self.update(True)

    def disable(self):
        return self.update(0)


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

    def kill(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.app.id, 'dynos', self.id)
        )

        r.raise_for_status()

        return r.ok
