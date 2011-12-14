# -*- coding: utf-8 -*-

"""
heroku.core
~~~~~~~~~~~

This module provides the base entrypoint for heroku.py.
"""

from .api import Heroku

def key(api_key):

    h = Heroku()

    # Login.
    h.authenticate(api_key)

    return h

def get_key(username, password):

    return Heroku().request_key(username, password)