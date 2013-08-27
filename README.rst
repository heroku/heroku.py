Heroku.py
=========

This is the updated Python wrapper for the Heroku API V3 (beta). The Heroku REST API
allows Heroku users to manage their accounts, applications, addons, and
other aspects related to Heroku. It allows you to easily utilize the Heroku
platform from your applications.

Introduction
===========

You can interact with the API as a pure api using the functionlity under the General API section,
or you can use the returned objects in an OO style, using the object API further down the page.
You can of course mix and match as you see fit.

Intro
-----

First instantiate a heroku_conn as above::
    
    import heroku
    heroku_conn = heroku.from_pass('kenneth@heroku.com', 'xxxxxxx')
    # or
    heroku_conn = heroku.from_key('YOUR_API_KEY')

Interact with your applications::

    >>> heroku_conn.apps
    [<app 'sharp-night-7758'>, <app 'empty-spring-4049'>, ...]

    >>> app = heroku_conn.apps['sharp-night-7758']

General notes on Debugging
--------------------------

Heroku provides some useful debugging information. This code exposes the following

Ratelimit Remaining
~~~~~~~~~~~~~~~~~~~

Get the current ratelimit remaining::

    num = heroku_conn.ratelimit_remaining()

Last Request Id
~~~~~~~~~~~~~~~

Get the unique ID of the last request sent to heroku to give them for debugging::

    id = heroku_conn.last_request_id


General notes about list Objects
--------------------------------

The new heroku API gives greater control over the interaction of the returned data. Primarily this 
centres around calls to the api which result in list objects being returned. 
e.g. multiple objects like apps, addons, releases etc.

You can control ordering, limits and pagination by supplying the following keywords::

    order_by=<'id'|'name'|'seq'>  
    limit=<num>
    valrange=<string> - See api docs for this

**You'll have to investigate the api for each object to work out which fields can be ordered by**

Examples
~~~~~~~~

List all apps in name order::

    heroku_conn.apps(order_by='name')

List the first 10 releases::

    heroku_conn.apps['empty-spring-4049'].releases(order_by='seq', limit=10)


General API
===========
Todo!!!


Object API
==========

Account
-------

Get account::

    account = heroku_conn.account()

List all configured keys::

    keylist = account.keys(order_by='id')

Add Key::

    account.add_key(<public_key_string>)

Remove key::

    account.remove_key(<public_key_string - or fingerprint>)

List all configured account "features" (otherwise known as "labs")::

    featurelist = account.features()

Disable a feature::

    feature = account.disable_feature(id_or_name)
    feature.disable()

Enable a feature::

    feature = account.enable_feature(id_or_name)
    feature.enable()

Addon Services
--------------

List all available Addon Services::

    addonlist = heroku_conn.addon_services(order_by='id')
    addonlist = heroku_conn.addon_services()

Get specific available Addon Service::

    addonservice = heroku_conn.addon_services(id_or_name)

App
--------

The App Class is the starting point for most of the api functionlity.
Although you can access most of this functionlity from the General API
without instantiating an App object. 

List all apps::

    applist = heroku_conn.apps(order_by='id')
    applist = heroku_conn.apps()

Get specific app::

    app = heroku_conn.app(id_or_name)
    app = heroku_conn.apps[id_or_name]

Destroy an app (**Warning this is irreversible**)::

    app.delete()

Addons
~~~~~~

List all Addons::

    addonlist = app.addons(order_by='id')
    addonlist = applist[id_or_name].addons(limit=10)

Install an Addon::

    addon = app.install_addon(plan_id=id, config={})
    addon = app.install_addon(plan_name=name, config={})
    addon = app.install_addon(plan_id=addonservice.id, config={})

Remove an Addon::

    addon = app.remove_addon(id)
    addon = app.remove_addon(addonservice.id)
    addon.delete()

Update/Upgrade an Addon::

    addon = addon.upgrade(name=<name>, config={})

App Labs/Features
~~~~~~~~~~~~~

List all features::

    appfeaturelist = app.features()
    appfeaturelist = app.labs() #nicename version
    appfeaturelist = app.features(order_by='id', limit=10)

Add a Feature::

    appfeature = app.enable_feature(feature_id_or_name)

Remove a Feature::

    appfeature = app.disable_feature(feature_id_or_name)

App Transfers
~~~~~~~~~~~~~

List all Transfers::

    transferlist = app.transfers()
    transferlist = app.transfers(order_by='id', limit=10)

Create a Transfer::

    transfer = app.create_transfer(id=<user_id>)
    transfer = app.create_transfer(email=<valid_email>)

Delete a Transfer::

    deletedtransfer = app.delete_transfer(transfer_id)
    deletedtransfer = app.delete_transfer(transfer_id)

Update a Transfer's state::

    transfer.update(state)
    transfer.update("Pending")
    transfer.update("Declined")
    transfer.update("Accepted")
    
    
Collaborators
~~~~~~~~~~~~~

List all Collaborators::

    collaboratorlist = app.collaborators()
    collaboratorlist = app.collaborators(order_by='id')

Add a Collaborator::

    collaborator = app.add_collaborator(email=<valid_email>, silent=0)
    collaborator = app.add_collaborator(id=user_id, silent=0)
    collaborator = app.add_collaborator(id=user_id, silent=1) #don't send invitation email

Remove a Collaborator::

    collaborator = app.remove_collaborator(userid_or_email)

ConfigVars
~~~~~~~~~~

Get an apps config::

    config = app.config()

Add a config Variable::

    config['New_var'] = 'new_val'

Update a config Variable::

    config['Existing_var'] = 'new_val'

Remove a config Variable::

    del config['Existing_var']
    config['Existing_var'] = None

Domains
~~~~~~~

Process Formation
~~~~~~~~~~~~~~~~~

Scale them up::

    >>> app.processes
    [<process 'web.1'>, <process 'worker.1'>]

    >>> app.processes['web']
    [<process 'web.1'>]

    >>> app.processes['web'].scale(3)
    [<process 'web.1'>, <process 'web.2'>, <process 'web.3'>]

    >>> app.processes[0].stop()
    True


Access the logs::

    >>> print app.logs(num=2)
    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from down to created
    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from created to starting

    >>> print app.logs(num=2, tail=True)
    <generator object stream_decode_response_unicode at 0x101151d20>


You can even stream the tail::

    >>> for line in app.logs(tail=True):
    ...     print line

    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from down to created
    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from created to starting
    ...


Change app configration::

    >>> app.config['DEBUG'] = 1
    >>> app.config
    {u'DEBUG': 1, u'PATH': u'bin:/usr/local/bin:/usr/bin:/bin', u'PYTHONUNBUFFERED': True}

    >>> del app.config['DEBUG']

See release history::

    >>> app.releases
    [<release 'v1'>, <release 'v2'>, ..., <release 'v84'>]


    >>> release = app.releases[-2]
    >>> release.name
    v84

    >>> release.env
    {u'PATH': u'bin:/usr/local/bin:/usr/bin:/bin', u'PYTHONUNBUFFERED': True}

    >>> release.pstable
    {u'web': u'gunicorn httpbin:app -b "0.0.0.0:$PORT"'}

    >>> release.addons
    [u'blitz:250', u'custom_domains:basic', u'logging:basic', u'releases:advanced']

    >>> release.rollback()
    <release 'v85'>

Create a new app::

    >>> cloud.apps.add('myapp')
    <app 'myapp'>

Delete the app completely::

    >>> app.destroy()
    True

And much more. Detailed docs forthcoming.


Customized Sessions
-------------------

Heroku.py is powered by `Requests <http://python-requests.org>`_ and supports all customized sessions:

For example advanced logging for easier debugging::

    >>> import sys
    >>> import requests
    >>> from heroku.api import Heroku

    >>> my_config = {'verbose': sys.stderr}
    >>> session = requests.session(config=my_config)
    >>> cloud = Heroku(session=session)
    >>> cloud.authenticate(cloud.request_key('kenneth@heroku.com', 'xxxxxxx'))
    >>> cloud.apps
    2011-12-21T22:53:47+00:00   GET   https://api.heroku.com/apps
    [<app 'myapp'>]


Installation
------------

To install ``heroku.py``, simply::

    $ pip install heroku

Or, if you absolutely must::

    $ easy_install heroku

But, you `really shouldn't do that <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.


License
-------

Copyright (c) 2013 Heroku, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
