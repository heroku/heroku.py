# -*- coding: utf-8 -*-

"""
heroku.core
~~~~~~~~~~~

This module provides the base entrypoint for heroku.py.
"""

from .api import Heroku
import requests

def from_key(api_key, **kwargs):
    """Returns an authenticated Heroku instance, via API Key."""

    h = Heroku(**kwargs)
    h.trust_env = False

    # Login.
    h.authenticate(api_key)

    return h

def from_pass(username, password):
    """Returns an authenticated Heroku instance, via password."""

    key = get_key(username, password)
    return from_key(key)

def from_env():
    """Returns an authenticated Heroku instance, via local netrc"""

    h = Heroku()
    h.trust_env = True

    # Pass fake value to authenticate with .netrc
    h.authenticate('nil')

    return h

def get_key(username, password):
    """Returns an API Key, fetched via password."""

    return Heroku().request_key(username, password)