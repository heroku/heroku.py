# -*- coding: utf-8 -*-

"""
heroku.core
~~~~~~~~~~~

This module provides the base entrypoint for heroku.py.
"""

from .api import Heroku

def from_key(api_key):
    """Returns an authenticated Heroku instance, via API Key."""

    h = Heroku()

    # Login.
    h.authenticate(api_key)

    return h

def from_pass(username, password):
    """Returns an authenticated Heroku instance, via password."""

    key = get_key(username, password)
    return from_key(key)

def get_key(username, password):
    """Returns an API Key, fetched via password."""

    return Heroku().request_key(username, password)