# -*- coding: utf-8 -*-

"""
heroku.models
~~~~~~~~~~~~~

This module contains the models that comprise the Heroku API.
"""

class BaseResource(object):
    def __init__(self):
        super(BaseResource, self).__init__()


class Addon(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class App(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Collaborator(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Config(BaseResource):
    def __init__(self):
        super(App, self).__init__()

class Domain(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Key(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Log(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Process(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Release(BaseResource):
    def __init__(self):
        super(App, self).__init__()


class Stack(BaseResource):
    def __init__(self):
        super(App, self).__init__()


