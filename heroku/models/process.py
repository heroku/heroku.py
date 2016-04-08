from baseresource import BaseResource
from ..structures import ProcessListResource


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
        Attach: If True it will return a rendezvous connection point,
        for streaming stdout/stderr
        Command: The actual command it will run
        """
        r = self._h._http_resource(
            method='POST',
            resource=('apps', self.app.name, 'ps',),
            data={'attach': attach, 'command': command}
        )

        r.raise_for_status()
        return self.app.processes[r.json()['process']]

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

        try:
            return self.app.processes[self.type]
        except KeyError:
            return ProcessListResource()


