from ..models import BaseResource, User, Stack
from ..rendezvous import Rendezvous
from ..structures import DynoListResource

from .addon import Addon
from .collaborator import Collaborator
from .configvars import ConfigVars
from .domain import Domain
from .dyno import Dyno
from .formation import Formation
from .logdrain import LogDrain
from .logsession import LogSession
from .region import Region
from .release import Release

from pprint import pprint # NOQA
import sys

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote # noqa


class App(BaseResource):
    """Heroku App."""

    _strs = ['buildpack_provided_description', 'git_url', 'id', 'name', 'web_url']
    _ints = ['slug_size', 'repo_size']
    _bools = ['maintenance']
    _dates = ['archived_at', 'created_at', 'released_at', 'updated_at']
    _map = {'region': Region, 'owner': User, 'stack': Stack}
    _pks = ['name', 'id']

    def __init__(self):
        super(App, self).__init__()

    def __repr__(self):
        return "<app '{0} - {1}'>".format(self.name, self.id)

    def addons(self, **kwargs):
        """
        Returns a list of your apps as app objects.
        """
        return self._h._get_resources(
            resource=('apps', self.name, 'addons'),
            obj=Addon, app=self, **kwargs
        )

    def delete(self):
        """
        Destroys the current app
        """
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id)
        )
        r.raise_for_status()
        return r.ok

    def add_collaborator(self, user_id_or_email, silent=False):
        """
        Adds a collaborator to your app
        [silent 1|0]  Specifies whether to email the collaborator or not
        """

        if silent:
            silent = True

        #commented out until api is fixed
        payload = {'silent': silent, 'user': user_id_or_email}

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'collaborators'),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Collaborator.new_from_dict(item, h=self._h, app=self)

    def remove_collaborator(self, id_or_email):
        """
        Removes a collaborator from a project
        options = id_or_email
        """
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.name, 'collaborators', id_or_email)
        )
        r.raise_for_status()

        return r.ok

    def install_addon(self, plan_id_or_name, config=None):

        payload = {}
        if not config:
            config = {}

        payload['plan'] = plan_id_or_name
        payload['config'] = config

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'addons'),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return Addon.new_from_dict(item, h=self._h, app=self)

    def remove_addon(self, id):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id, 'addons', id),
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

    def update_config(self, config):
        payload = self._h._resource_serialize(config)
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.id, 'config-vars'),
            data=payload
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return ConfigVars.new_from_dict(item, h=self._h, app=self)

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

    def kill_dyno(self, dyno_id_or_name):
        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id, 'dynos', quote(dyno_id_or_name))
        )

        r.raise_for_status()

        return r.ok

    def restart(self):
        for dyno in self.dynos():
            if dyno.type != 'run':
                dyno.kill()
        return self

    def run_command_detached(self, command, size=1, env=None):
        """Run a remote command but do not wait for the command to complete"""
        return self.run_command(command, attach=False, printout=False, size=size, env=env)

    def run_command(self, command, attach=True, printout=True, size=1, env=None):
        """Run a remote command attach=True if you want to capture the output"""
        if attach:
            attach = True

        payload = {'command': command, 'attach': attach, 'size': size}
        if env:
            payload['env'] = env

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
            obj=Formation, app=self, **kwargs
        )

    def scale_formation_process(self, formation_id_or_name, quantity):
        assert(quantity == 0 or quantity)
        payload = {}
        payload['quantity'] = quantity

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.id, 'formation', formation_id_or_name),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        return self._h._process_item(self._h._resource_deserialize(r.content.decode("utf-8")), Formation)

    def resize_formation_process(self, formation_id_or_name, size):
        assert(size == 0 or size)
        payload = {}
        payload['size'] = size

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.id, 'formation', formation_id_or_name),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        return self._h._process_items(self._h._resource_deserialize(r.content.decode("utf-8")), Formation)

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
        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.id, 'features', id_or_name),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AppFeature.new_from_dict(item, h=self._h, app=self)

    def logdrains(self, **kwargs):
        return self._h._get_resources(
            resource=('apps', self.id, 'log-drains'),
            obj=LogDrain, app=self, **kwargs
        )

    def create_logdrain(self, url):

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.id, 'log-drains'),
            data=self._h._resource_serialize({'url': url})
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return LogDrain.new_from_dict(item, h=self._h, app=self)

    def remove_logdrain(self, id_or_url):

        r = self._h._http_resource(
            method='DELETE',
            resource=('apps', self.id, 'log-drains', id_or_url),
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return LogDrain.new_from_dict(item, h=self._h, app=self)

    def rename(self, name):
        """Renames app to given name."""

        return self.update(name=name)

    def transfers(self, **kwargs):
        return self._h._get_resources(
            resource=('account', 'app-transfers'),
            obj=AppTransfer, app=self, **kwargs
        )

    def create_transfer(self, recipient_id_or_name):
        """Transfers app to given username's account."""

        payload = {'app': self.id, 'recipient': recipient_id_or_name}

        r = self._h._http_resource(
            method='PUT',
            resource=('account', 'app-transfers'),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AppTransfer.new_from_dict(item, h=self._h, app=self)

    def delete_transfer(self, id):
        r = self._h._http_resource(
            method='DELETE',
            resource=('account', 'app-transfers', id),
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AppTransfer.new_from_dict(item, h=self._h, app=self)

    def enable_maintenance_mode(self):
        """Enables maintenance mode."""
        return self.update(maintenance=True)

    def disable_maintenance_mode(self):
        """Disables maintenance mode."""
        return self.update(maintenance=0)

    def update(self, maintenance=False, name=None):

        assert(maintenance or name or maintenance == 0)

        payload = {}
        if name:
            payload['name'] = name
        else:
            if maintenance or maintenance == 0:
                payload['maintenance'] = maintenance

        r = self._h._http_resource(
            method='PATCH',
            resource=('apps', self.id),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return App.new_from_dict(item, h=self._h, app=self)

    def destroy(self):
        """Destoys the app. Do be careful."""
        return self.delete()

    def stream_log(self, dyno=None, lines=100, source=None, timeout=False):
        logger = self._logger(dyno=dyno, lines=lines, source=source, tail=True)

        return logger.stream(timeout=timeout)

    def get_log(self, dyno=None, lines=100, source=None, timeout=False):
        logger = self._logger(dyno=dyno, lines=lines, source=source, tail=0)

        return logger.get(timeout=timeout)

    def _logger(self, dyno=None, lines=100, source=None, tail=0):

        payload = {}
        if dyno:
            payload['dyno'] = dyno

        if tail:
            payload['tail'] = tail

        if source:
            payload['source'] = source

        if lines:
            payload['lines'] = lines

        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.id, 'log-sessions'),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))

        return LogSession.new_from_dict(item, h=self._h, app=self)

    def releases(self, **kwargs):
        """The releases for this app."""
        return self._h._get_resources(
            resource=('apps', self.name, 'releases'),
            obj=Release, app=self, **kwargs
        )

    def rollback(self, release):
        """Rolls back the release to the given version."""
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.name, 'releases'),
            params={'rollback': release},
            legacy=True
        )
        r.raise_for_status()
        return self.releases()[-1]


class AppTransfer(BaseResource):
    _strs = ['id', 'state']
    _map = {'app': App, 'recipient': User, 'owner': User}
    _dates = ['created_at', 'updated_at']
    _pks = ['id']

    def __init__(self):
        self.app = None
        super(AppTransfer, self).__init__()

    def __repr__(self):
        return "<apptransfer '{0}'>".format(self.id)

    def update(self, state):

        payload = {}
        payload['state'] = state

        r = self._h._http_resource(
            method='PATCH',
            resource=('account', 'app-transfers', self.id),
            data=self._h._resource_serialize(payload)
        )
        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AppTransfer.new_from_dict(item, h=self._h, app=self)

    def delete(self):
        r = self._h._http_resource(
            method='DELETE',
            resource=('account', 'app-transfers', self.id),
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return AppTransfer.new_from_dict(item, h=self._h, app=self)


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
