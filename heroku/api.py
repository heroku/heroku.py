# -*- coding: utf-8 -*-

"""
heroku.api
~~~~~~~~~~

This module provides the basic API interface for Heroku.
"""

from .compat import json
from .helpers import is_collection
from .models import Plan, RateLimit
from .models.app import App
from .models.addon import Addon
from .models.account import Account
from .models.key import Key
from .models.configvars import ConfigVars
from .models.logsession import LogSession
from .structures import KeyedListResource, SSHKeyListResource
from .models.account.feature import AccountFeature
from requests.exceptions import HTTPError
from pprint import pprint # noqa
import requests
import sys

if sys.version_info > (3, 0):
    from urllib.parse import quote
else:
    from urllib import quote # noqa


HEROKU_URL = 'https://api.heroku.com'


class RateLimitExceeded(Exception):
    pass


class MaxRangeExceeded(Exception):
    pass


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
        self._last_request_id = None

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

    @property
    def is_authenticated(self):
        if self._api_key_verified is None:
            return self._verify_api_key()
        else:
            return self._api_key_verified

    def _verify_api_key(self):
        r = self._session.get(self._url_for('account/rate-limits'))

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

    def _get_headers_for_request(self, method, url, legacy=False, order_by=None, limit=None, valrange=None, sort=None):
        headers = {}
        if legacy is True:
            #Nasty patch session to fallback to old api
            headers.update({'Accept': 'application/json'})

        else:
            range_str = None
            if order_by or limit or valrange or sort:
                range_str = ""
                if order_by:
                    range_str = "{0} ..".format(order_by)
                if limit:
                    if limit > 1000:
                        raise MaxRangeExceeded("Your *limit* ({0}) argument is greater than the maximum allowed value of 1000".format(limit))
                    range_str += "; max={0}".format(limit)
                if not sort is None:
                    assert(sort == 'asc' or sort == 'desc')
                    range_str += "; order={0}".format(sort)

                if valrange:
                    #If given, This should override limit and order_by
                    range_str = valrange

            if not range_str == None:
                headers.update({'Range': range_str})

        return headers

    def _http_resource(self, method, resource, params=None, data=None, legacy=False, order_by=None, limit=None, valrange=None, sort=None):
        """Makes an HTTP request."""

        if not is_collection(resource):
            resource = [resource]

        url = self._url_for(*resource)

        headers = self._get_headers_for_request(method, url, legacy=legacy, order_by=order_by, limit=limit, valrange=valrange, sort=sort)

        r = self._session.request(method, url, params=params, data=data, headers=headers)

        if 'ratelimit-remaining' in r.headers:
            self._ratelimit_remaining = r.headers['ratelimit-remaining']

        if 'Request-Id' in r.headers:
            self._last_request_id = r.headers['Request-Id']

        #if 'Accept-Ranges' in r.headers:
            #print "Accept-Ranges = {0}".format(r.headers['Accept-Ranges'])

        if r.status_code == 422:
            http_error = HTTPError('%s - %s Client Error: %s' %
                                   (self._last_request_id, r.status_code, r.content.decode("utf-8")))
            http_error.response = r
            raise http_error

        if r.status_code == 429:
            #Rate limit reached
            print r.headers
            raise RateLimitExceeded("You have exceeded your rate limit \n{0}".format(r.content.decode("utf-8")))

        if (not str(r.status_code).startswith('2')) and (not r.status_code in [304]):
            print "Status not sensible - {0}".format(r.status_code)
            print r.headers
            print r.content.decode("utf-8")
            pass
        r.raise_for_status()

        return r

    def _get_resource(self, resource, obj, params=None, **kwargs):
        """Returns a mapped object from an HTTP resource."""
        r = self._http_resource('GET', resource, params=params)

        return self._process_item(self._resource_deserialize(r.content.decode("utf-8")), obj, **kwargs)

    def _process_item(self, item, obj, **kwargs):

        return obj.new_from_dict(item, h=self, **kwargs)

    def _get_resources(self, resource, obj, params=None, map=None, legacy=None, order_by=None, limit=None, valrange=None, sort=None, **kwargs):
        """Returns a list of mapped objects from an HTTP resource."""
        if not order_by:
            order_by = obj.order_by

        return self._process_items(self._get_data(resource, params=params, legacy=legacy, order_by=order_by, limit=limit, valrange=valrange, sort=sort), obj, map=map, **kwargs)

    def _get_data(self, resource, params=None, legacy=None, order_by=None, limit=None, valrange=None, sort=None):

        r = self._http_resource('GET', resource, params=params, legacy=legacy, order_by=order_by, limit=limit, valrange=valrange, sort=sort)

        items = self._resource_deserialize(r.content.decode("utf-8"))
        if r.status_code == 206 and 'Next-Range' in r.headers and not limit:
            #We have unexpected chunked response - deal with it
            valrange = r.headers['Next-Range']
            print "Warning Response was chunked, Loading the next Chunk using the following next-range header returned by Heroku '{0}'. WARNING - This breaks randomly depending on your order_by name. I think it's only guarenteed to work with id's - Looks to be a Heroku problem".format(valrange)
            new_items = self._get_data(resource, params=params, legacy=legacy, order_by=order_by, limit=limit, valrange=valrange, sort=sort)
            items.extend(new_items)

        return items

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

    def account(self):
        return self._get_resource(('account'), Account)

    def addons(self, app_id_or_name, **kwargs):
        return self._get_resources(resource=('apps', app_id_or_name, 'addons'), obj=Addon, **kwargs)

    def addon_services(self, id_or_name=None, **kwargs):
        if id_or_name is not None:
            return self._get_resource(('addon-services/{0}'.format(quote(id_or_name))), Plan)
        else:
            return self._get_resources(('addon-services'), Plan, **kwargs)

    def apps(self, **kwargs):
        return self._get_resources(('apps'), App, **kwargs)

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

    def keys(self, **kwargs):
        return self._get_resources(('user', 'keys'), Key, map=SSHKeyListResource, **kwargs)

    def labs(self, **kwargs):
        return self.features(**kwargs)

    def features(self, **kwargs):
        return self._get_resources(('account/features'), AccountFeature, **kwargs)

    @property
    def rate_limit(self):
        return self._get_resource(('account/rate-limits'), RateLimit)

    def ratelimit_remaining(self):

        if self._ratelimit_remaining is not None:
            return int(self._ratelimit_remaining)
        else:
            self.rate_limit
            return int(self._ratelimit_remaining)

    def stream_app_log(self, app_id_or_name, dyno=None, lines=100, source=None, timeout=False):
        logger = self._app_logger(app_id_or_name, dyno=dyno, lines=lines, source=source, tail=True)

        return logger.stream(timeout=timeout)

    def get_app_log(self, app_id_or_name, dyno=None, lines=100, source=None, timeout=False):
        logger = self._app_logger(app_id_or_name, dyno=dyno, lines=lines, source=source, tail=0)

        return logger.get(timeout=timeout)

    def update_appconfig(self, app_id_or_name, config):
        payload = self._resource_serialize(config)
        r = self._http_resource(
            method='PATCH',
            resource=('apps', app_id_or_name, 'config-vars'),
            data=payload
        )

        r.raise_for_status()
        item = self._resource_deserialize(r.content.decode("utf-8"))
        return ConfigVars.new_from_dict(item, h=self)

    def _app_logger(self, app_id_or_name, dyno=None, lines=100, source=None, tail=0):
        payload = {}
        if dyno:
            payload['dyno'] = dyno

        if tail:
            payload['tail'] = tail

        if source:
            payload['source'] = source

        if lines:
            payload['lines'] = lines

        r = self._http_resource(
            method='POST',
            resource=('apps', app_id_or_name, 'log-sessions'),
            data=self._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._resource_deserialize(r.content.decode("utf-8"))

        return LogSession.new_from_dict(item, h=self, app=self)

    @property
    def last_request_id(self):
        return self._last_request_id


class ResponseError(ValueError):
    """The API Response was unexpected."""
