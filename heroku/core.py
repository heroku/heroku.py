# -*- coding: utf-8 -*-

"""
heroku.core
~~~~~~~~~~~

This module provides the base entrypoint for heroku.py.
"""

from .api import Heroku

def login(api_key):

    h = Heroku()

    # Login.
    h.login(api_key)

    return h