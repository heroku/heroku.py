# -*- coding: utf-8 -*-

"""
heroku.core
~~~~~~~~~~~

This module provides the base entrypoint for heroku.py.
"""

from .api import Heroku


def from_key(api_key, **kwargs):
    """Returns an authenticated Heroku instance, via API Key."""

    h = Heroku(**kwargs)

    # Login.
    h.authenticate(api_key)

    return h
