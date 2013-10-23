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
from .models.dyno import Dyno
from .models.account import Account
from .models.key import Key
from .models.configvars import ConfigVars
from .models.logsession import LogSession
from .models.oauth import OAuthClient, OAuthAuthorization, OAuthToken
from .rendezvous import Rendezvous
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

        #print "\n\n\n\n"
        #print url
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
        #print r.content.decode("utf-8")
        #print "\n\n\n\n"
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

        if not isinstance(d_items, list):
            print "Warning, Response for '{0}' was of type {1} - I was expecting a 'list'. This could mean the api has changed its response type for this request.".format(obj, type(d_items))
            if isinstance(d_items, dict):
                print "As it's a dict, I'll try to process it anyway"
                return self._process_item(d_items, obj, **kwargs)

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

    def create_app(self, name=None, stack_id_or_name='cedar', region_id_or_name=None):
        """Creates a new app."""

        payload = {}

        if name:
            payload['name'] = name

        if stack_id_or_name:
            payload['stack'] = stack_id_or_name

        if region_id_or_name:
            payload['region'] = region_id_or_name

        try:
            r = self._http_resource(
                method='POST',
                resource=('apps',),
                data=self._resource_serialize(payload)
            )
            r.raise_for_status()
            item = self._resource_deserialize(r.content.decode("utf-8"))
            app = App.new_from_dict(item, h=self)
        except HTTPError as e:
            if "Name is already taken" in str(e):
                print "Warning - {0:s}".format(e)
                app = self.app(name)
                pass
            else:
                raise e
        return app

    def keys(self, **kwargs):
        return self._get_resources(('user', 'keys'), Key, map=SSHKeyListResource, **kwargs)

    def labs(self, **kwargs):
        return self.features(**kwargs)

    def features(self, **kwargs):
        return self._get_resources(('account/features'), AccountFeature, **kwargs)

    def oauthauthorization(self, oauthauthorization_id):
        return self._get_resource(('oauth', 'authorizations', oauthauthorization_id), OAuthAuthorization)

    def oauthauthorizations(self, **kwargs):
        return self._get_resources(('oauth', 'authorizations'), OAuthAuthorization, **kwargs)

    def oauthauthorization_create(self, scope, oauthclient_id=None, description=None):
        """
        Creates an OAuthAuthorization
        """

        payload = {'scope': scope}
        if oauthclient_id:
            payload.update({'client': oauthclient_id})

        if description:
            payload.update({'description': description})

        r = self._http_resource(
            method='POST',
            resource=('oauth', 'authorizations'),
            data=self._h._resource_serialize(payload)
        )
        r.raise_for_status()
        item = self._resource_deserialize(r.content.decode("utf-8"))
        return OAuthClient.new_from_dict(item, h=self)

    def oauthauthorization_delete(self, oauthauthorization_id):
        """
        Destroys the OAuthAuthorization with oauthauthorization_id
        """
        r = self._http_resource(
            method='DELETE',
            resource=('oauth', 'authorizations', oauthauthorization_id)
        )
        r.raise_for_status()
        return r.ok

    def oauthclient(self, oauthclient_id):
        return self._get_resource(('oauth', 'clients', oauthclient_id), OAuthClient)

    def oauthclients(self, **kwargs):
        return self._get_resources(('oauth', 'clients'), OAuthClient, **kwargs)

    def oauthclient_create(self, name, redirect_uri):
        """
        Creates an OAuthClient with the given name and redirect_uri
        """

        payload = {'name': name, 'redirect_uri': redirect_uri}

        r = self._http_resource(
            method='POST',
            resource=('oauth', 'clients'),
            data=self._h._resource_serialize(payload)
        )
        r.raise_for_status()
        item = self._resource_deserialize(r.content.decode("utf-8"))
        return OAuthClient.new_from_dict(item, h=self)

    def oauthclient_delete(self, oauthclient_id):
        """
        Destroys the OAuthClient with id oauthclient_id
        """
        r = self._http_resource(
            method='DELETE',
            resource=('oauth', 'clients', oauthclient_id)
        )
        r.raise_for_status()
        return r.ok

    def oauthtoken_create(self, client_secret=None, grant_code=None, grant_type=None, refresh_token=None):
        """
        Creates an OAuthToken with the given optional parameters
        """

        payload = {}
        grant = {}
        if client_secret:
            payload.update({'client': {'secret': client_secret}})

        if grant_code:
            grant.update({'code': grant_code})

        if grant_type:
            grant.update({'type': grant_type})

        if refresh_token:
            payload.update({'refresh_token': {'token': refresh_token}})

        if grant:
            payload.update({'grant': grant})

        r = self._http_resource(
            method='POST',
            resource=('oauth', 'tokens'),
            data=self._h._resource_serialize(payload)
        )
        r.raise_for_status()
        item = self._resource_deserialize(r.content.decode("utf-8"))
        return OAuthToken.new_from_dict(item, h=self)

    def run_command_on_app(self, appname, command, size=1, attach=True, printout=True, env=None):
        """Run a remote command attach=True if you want to capture the output"""
        if attach:
            attach = True
        payload = {'command': command, 'attach': attach, 'size': size}

        if env:
            payload['env'] = env

        r = self._http_resource(
            method='POST',
            resource=('apps', appname, 'dynos'),
            data=self._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._resource_deserialize(r.content.decode("utf-8"))
        dyno = Dyno.new_from_dict(item, h=self)

        if attach:
            output = Rendezvous(dyno.attach_url, printout).start()
            return output, dyno
        else:
            return dyno

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
