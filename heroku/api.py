# -*- coding: utf-8 -*-

"""
heroku.api
~~~~~~~~~~

This module provides the basic API interface for Heroku.
"""

from .compat import json
from .helpers import is_collection
from .models import * # noqa
from .structures import KeyedListResource
from heroku.models import Feature
from requests.exceptions import HTTPError
import requests

HEROKU_URL = 'https://api.heroku.com'


class HerokuCore(object):
    """The core Heroku class."""
    def __init__(self, session=None):
        super(HerokuCore, self).__init__()
        if session is None:
            session = requests.session()

        #: The User's API Key.
        self._api_key = None
        self._api_key_verified = None
        self._heroku_url = HEROKU_URL
        self._session = session
        self._ratelimit_remaining = None

        # We only want JSON back.
        #self._session.headers.update({'Accept': 'application/json'})
        self._session.headers.update({'Accept': 'application/vnd.heroku+json; version=3', 'Content-Type': 'application/json'})

    def __repr__(self):
        return '<heroku-core at 0x%x>' % (id(self))

    def authenticate(self, api_key):
        """Logs user into Heroku with given api_key."""
        self._api_key = api_key

        # Attach auth to session.
        self._session.auth = ('', self._api_key)

        return self._verify_api_key()

    def request_key(self, username, password):
        r = self._http_resource(
            method='POST',
            resource=('login'),
            data={'username': username, 'password': password}
        )
        r.raise_for_status()

        return json.loads(r.content.decode("utf-8")).get('api_key')

    @property
    def is_authenticated(self):
        if self._api_key_verified is None:
            return self._verify_api_key()
        else:
            return self._api_key_verified

    def _verify_api_key(self):
        r = self._session.get(self._url_for('apps'))

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

    def _http_resource(self, method, resource, params=None, data=None, legacy=False):
        """Makes an HTTP request."""

        if not is_collection(resource):
            resource = [resource]

        url = self._url_for(*resource)
        print url
        from pprint import pprint
        #pprint(method)
        #pprint(params)
        pprint(data)
        #pprint(r.headers)
        if legacy is True:
            #Nasty patch session to fallback to old api
            self._session.headers.update({'Accept': 'application/json'})
            del self._session.headers['Content-Type']
            pass
        pprint(self._session.headers)
        r = self._session.request(method, url, params=params, data=data)
        if legacy is True:
            #Nasty patch session to return to the new api
            self._session.headers.update({'Accept': 'application/vnd.heroku+json; version=3', 'Content-Type': 'application/json'})
            pass
        self._ratelimit_remaining = r.headers['ratelimit-remaining']

        if r.status_code == 422:
            http_error = HTTPError('%s Client Error: %s' %
                                   (r.status_code, r.content.decode("utf-8")))
            http_error.response = r
            raise http_error

        if r.status_code != 200 or r.status_code != 304:
            print r.content.decode("utf-8")
        r.raise_for_status()

        return r

    def _get_resource(self, resource, obj, params=None, **kwargs):
        """Returns a mapped object from an HTTP resource."""
        r = self._http_resource('GET', resource, params=params)

        return self._process_item(self._resource_deserialize(r.content.decode("utf-8")), obj, **kwargs)

    def _process_item(self, item, obj, **kwargs):

        return obj.new_from_dict(item, h=self, **kwargs)

    def _get_resources(self, resource, obj, params=None, map=None, **kwargs):
        """Returns a list of mapped objects from an HTTP resource."""
        r = self._http_resource('GET', resource, params=params)
        return self._process_items(self._resource_deserialize(r.content.decode("utf-8")), obj, map=map, **kwargs)

    def _process_items(self, d_items, obj, map=None, **kwargs):

        items = [obj.new_from_dict(item, h=self, **kwargs) for item in d_items]

        if map is None:
            map = KeyedListResource

        list_resource = map(items=items)
        list_resource._h = self
        list_resource._obj = obj
        list_resource._kwargs = kwargs

        return list_resource


class Heroku(HerokuCore):
    """The main Heroku class."""

    def __init__(self, session=None):
        super(Heroku, self).__init__(session=session)

    def __repr__(self):
        return '<heroku-client at 0x%x>' % (id(self))

    @property
    def account(self):
        return self._get_resource(('account'), Account)

    @property
    def addons(self):
        return self._get_resources(('addons'), Addon)

    def addon_services(self, id_or_name=None):
        if id_or_name is not None:
            return self._get_resource(('addon-services/{0}'.format(quote(id_or_name))), AvailableAddon)
        else:
            return self._get_resources(('addon-services'), AvailableAddon)

    @property
    def apps(self):
        return self._get_resources(('apps'), App)

    def app(self, id_or_name):
        return self._get_resource(('apps/{0:s}'.format(id_or_name)), App)

    def create_app(self, name=None, stack='cedar', region_id=None, region_name=None):
        """Creates a new app."""

        payload = {}
        region = {}

        if name:
            payload['name'] = name

        if stack:
            payload['stack'] = stack

        if region_id:
            region['id'] = region_id
        if region_name:
            region['name'] = region_name
        if region_id or region_name:
            payload['region'] = region
            pass

        print payload
        try:
            r = self._http_resource(
                method='POST',
                resource=('apps',),
                data=self._resource_serialize(payload)
            )
            name = json.loads(r.content).get('name')
        except HTTPError as e:
            if "Name is already taken" in str(e):
                print "Warning - {0:s}".format(e)
                pass
            else:
                raise e
        return self.app(name)

    @property
    def keys(self):
        return self._get_resources(('user', 'keys'), Key, map=SSHKeyListResource)

    @property
    def labs(self):
        return self._get_resources(('account/features'), Feature, map=filtered_key_list_resource_factory(lambda obj: obj.kind == 'user'))

    @property
    def rate_limit(self):
        return self._get_resource(('account/rate-limits'), RateLimit)

    def ratelimit_remaining(self):

        if self._ratelimit_remaining is not None:
            return self._ratelimit_remaining
        else:
            self.rate_limit
            return self._ratelimit_remaining


class ResponseError(ValueError):
    """The API Response was unexpected."""
