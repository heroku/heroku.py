# -*- coding: utf-8 -*-

"""
heroku.api
~~~~~~~~~~

This module provides the basic API interface for Heroku.
"""

import requests


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
        return '/'.join([self._heroku_url] + list(args))


class Heroku(HerokuCore):
    """The main Heroku class."""

    def __init__(self):
        super(Heroku, self).__init__()

    def __repr__(self):
        return '<heroku-client at 0x%x>' % (id(self))

    def apps(self):
        print self._url_for('apps')



class ResponseError(ValueError):
    """The API Response was unexpected."""