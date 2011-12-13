# -*- coding: utf-8 -*-

"""
heroku.api
~~~~~~~~~~

This module provides the basic API interface for Heroku.
"""

import requests
from .compat import json
from .models import *

HEROKU_URL = 'https://api.heroku.com'


class HerokuCore(object):
    """The core Heroku class."""
    def __init__(self):
        super(HerokuCore, self).__init__()

        #: The User's API Key.
        self._api_key = None
        self._api_key_verified = None
        self._s = requests.session()
        self._heroku_url = HEROKU_URL

        # We only want JSON back.
        self._s.headers.update({'Accept': 'application/json'})

    def __repr__(self):
        return '<heroku-core at 0x%x>' % (id(self))

    def login(self, api_key):
        """Logs user into Heroku with given api_key."""
        self._api_key = api_key

        # Attach auth to session.
        self._s.auth = ('', self._api_key)

        return self._verify_api_key()

    @property
    def is_authenticated(self):
        if self._api_key_verified is None:
            return self._verify_api_key()
        else:
            return self._api_key_verified

    def _verify_api_key(self):
        r = self._s.get(self._url_for('apps'))

        self._api_key_verified = True if r.ok else False

        return self._api_key_verified

    def _url_for(self, *args):
        args = map(str, args)
        return '/'.join([self._heroku_url] + list(args))

    @staticmethod
    def _resource_serialize(o):
        """Returns JSON serialization of given object."""
        return json.dumps(o)

    @staticmethod
    def _resource_deserialize(s):
        """Returns dict deserialization of a given JSON string."""

        try:
            return json.loads(s)
        except ValueError:
            raise ResponseError('The API Response was not valid.')


    def _get_resource(self, resource, obj, **kwargs):

        url = self._url_for(*resource)

        r = self._s.get(url, params=kwargs)

        item = self._resource_deserialize(r.content)

        return obj.new_from_dict(item, h=self)


    def _get_resources(self, resource, obj, **kwargs):

        url = self._url_for(*resource)

        r = self._s.get(url, params=kwargs)

        d_items = self._resource_deserialize(r.content)

        return [obj.new_from_dict(item, h=self) for item in d_items]


class Heroku(HerokuCore):
    """The main Heroku class."""

    def __init__(self):
        super(Heroku, self).__init__()

    def __repr__(self):
        return '<heroku-client at 0x%x>' % (id(self))

    def addons(self):
        return self._get_resources(('addons'), Addon)

    def apps(self):
        return self._get_resources(('apps'), App)

    def get_app(self, name):
        return self._get_resource(('apps', name), App)



class ResponseError(ValueError):
    """The API Response was unexpected."""