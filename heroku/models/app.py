from .. structures import *
import json
import requests
from baseresource import BaseResource


class App(BaseResource):
    """Heroku App."""

    _strs = ['name', 'create_status', 'stack', 'repo_migrate_status']
    _ints = ['id', 'slug_size', 'repo_size', 'dynos', 'workers']
    _dates = ['created_at']
    _pks = ['name', 'id']

    def __init__(self):
        super(App, self).__init__()

    def __repr__(self):
        return "<app '{0}'>".format(self.name)

    def new(self, name=None, stack='cedar', region=None):
        """Creates a new app."""

        payload = {}

        if name:
            payload['app[name]'] = name

        if stack:
            payload['app[stack]'] = stack

        if region:
            payload['app[region]'] = region

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
            obj=Feature,
            params={'app': self.name},
            app=self,
            map=filtered_key_list_resource_factory(
                lambda item: item.kind == 'app'
            )
        )

    def rollback(self, release):
        """Rolls back the release to the given version."""
        self._h._http_resource(
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


