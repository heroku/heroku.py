# -*- coding: utf-8 -*-

"""
heroku.api
~~~~~~~~~~

This module provides the basic API interface for Heroku.
"""

import requests
from .compat import json
from .helpers import is_collection
from .structures import KeyedListResource
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

    def authenticate(self, api_key):
        """Logs user into Heroku with given api_key."""
        self._api_key = api_key

        # Attach auth to session.
        self._s.auth = ('', self._api_key)

        return self._verify_api_key()

    def request_key(self, username, password):
        r = self._http_resource(
            method='POST',
            resource=('login'),
            data={'username': username, 'password': password}
        )
        r.raise_for_status()

        return json.loads(r.content).get('api_key')

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

    def _http_resource(self, method, resource, params=None, data=None):
        """Makes an HTTP request."""

        if not is_collection(resource):
            resource = [resource]

        url = self._url_for(*resource)
        r = self._s.request(method, url, params=params, data=data)

        # TODO: check heroku's status codes
        r.raise_for_status()

        return r

    def _get_resource(self, resource, obj, params=None, **kwargs):
        """Returns a mapped object from an HTTP resource."""
        r = self._http_resource('GET', resource, params=params)
        item = self._resource_deserialize(r.content)

        return obj.new_from_dict(item, h=self, **kwargs)

    def _get_resources(self, resource, obj, params=None, map=None, **kwargs):
        """Returns a list of mapped objects from an HTTP resource."""
        r = self._http_resource('GET', resource, params=params)
        d_items = self._resource_deserialize(r.content)

        items =  [obj.new_from_dict(item, h=self, **kwargs) for item in d_items]

        if map is None:
            map = KeyedListResource

        list_resource = map(items=items)
        list_resource._h = self
        list_resource._obj = obj

        return list_resource


class Heroku(HerokuCore):
    """The main Heroku class."""

    def __init__(self):
        super(Heroku, self).__init__()

    def __repr__(self):
        return '<heroku-client at 0x%x>' % (id(self))

    @property
    def addons(self):
        return self._get_resources(('addons'), Addon)

    @property
    def apps(self):
        return self._get_resources(('apps'), App)

    @property
    def keys(self):
        return self._get_resources(('user', 'keys'), Key, map=SSHKeyListResource)


class ResponseError(ValueError):
    """The API Response was unexpected."""