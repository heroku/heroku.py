# -*- coding: utf-8 -*-

"""
heroku.compat
~~~~~~~~~~~~~

Compatiblity for heroku.py.
"""

try:
    import json
except ImportError:
    import simplejson as json