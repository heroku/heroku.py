Heroku.py
=========

This is the updated Python wrapper for the Heroku `API V3 (beta). <https://devcenter.heroku.com/articles/platform-api-reference>`_ 
The Heroku REST API allows Heroku users to manage their accounts, applications, addons, and
other aspects related to Heroku. It allows you to easily utilize the Heroku
platform from your applications.

Introduction
===========

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

Throughout the docs you'll see references to using limit & order_by. Wherever you see these, you *should* be able to use *limit*, *order_by* and *valrange*.

You can control ordering, limits and pagination by supplying the following keywords::

    order_by=<'id'|'seq'>  
    limit=<num>
    valrange=<string> - See api docs for this, This value is passed straight through to the API call *as is*.

**You'll have to investigate the api for each object's *Accept-Ranges* header to work out which fields can be ordered by**

Examples
~~~~~~~~

List all apps in name order::

    heroku_conn.apps(order_by='name')

List the first 10 releases::

    app.releases(order_by='seq', limit=10)
    heroku_conn.apps()['empty-spring-4049'].releases(order_by='seq', limit=10)


List objects can be referred to directly by *any* of their primary keys too::

    app = heroku_conn.apps()['myapp']
    dyno = heroku_conn.apps()['myapp_id'].dynos()['web.1']
    proc = heroku_conn.apps()['my_app'].process_formation()['web']

**Be careful if you use *limit* in a list call *and* refer directly to an primary key** 
E.g.Probably stupid...::

    dyno = heroku_conn.apps()['myapp'].dynos(limit=1)['web.1']
    
General Notes on Objects
------------------------

To find out the Attributes available for a given object, look at the corresponding Documentation for that object.
e.g.

`Formation <https://devcenter.heroku.com/articles/platform-api-reference#formation>`_ Object::

    >>>print feature.command
    bundle exec rails server -p $PORT
    
    >>>print feature.created_at
    2012-01-01T12:00:00Z

    >>>print feature.id
    01234567-89ab-cdef-0123-456789abcdef

    >>>print feature.quantity
    1
    >>>print feature.size
    1
    >>>print feature.type
    web

    >>>print feature.updated_at
    2012-01-01T12:00:00Z

Legacy API Calls
================

The API has been built with an internal legacy=True ability, so any functionlity not implemented in the new API can be called via the previous `legacy API <https://legacy-api-docs.herokuapp.com/>`_. This is currently only used for *rollbacks*.


Object API
==========

Account
-------

Get account::

    account = heroku_conn.account()

Change Password::

    account.change_password("<current_password>", "<new_password>")

SSH Keys
~~~~

List all configured keys::

    keylist = account.keys(order_by='id')

Add Key::

    account.add_key(<public_key_string>)

Remove key::

    account.remove_key(<public_key_string - or fingerprint>)

Account Features (Heroku Labs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List all configured account "features"::

    featurelist = account.features()

Disable a feature::

    feature = account.disable_feature(id_or_name)
    feature.disable()

Enable a feature::

    feature = account.enable_feature(id_or_name)
    feature.enable()

Plans - or Addon Services
--------------

List all available Addon Services::

    addonlist = heroku_conn.addon_services(order_by='id')
    addonlist = heroku_conn.addon_services()

Get specific available Addon Service::

    addonservice = heroku_conn.addon_services(<id_or_name>)

App
--------

The App Class is the starting point for most of the api functionlity.

List all apps::

    applist = heroku_conn.apps(order_by='id')
    applist = heroku_conn.apps()

Get specific app::

    app = heroku_conn.app(<id_or_name>)
    app = heroku_conn.apps[id_or_name]

Destroy an app (**Warning this is irreversible**)::

    app.delete()

Addons
~~~~~~

List all Addons::

    addonlist = app.addons(order_by='id')
    addonlist = applist[<id_or_name>].addons(limit=10)

Install an Addon::

    addon = app.install_addon(plan_id='<id>', config={})
    addon = app.install_addon(plan_name='<name>', config={})
    addon = app.install_addon(plan_id=addonservice.id, config={})

Remove an Addon::

    addon = app.remove_addon(<id>)
    addon = app.remove_addon(addonservice.id)
    addon.delete()

Update/Upgrade an Addon::

    addon = addon.upgrade(name='<name>', config={})

App Labs/Features
~~~~~~~~~~~~~

List all features::

    appfeaturelist = app.features()
    appfeaturelist = app.labs() #nicename for features()
    appfeaturelist = app.features(order_by='id', limit=10)

Add a Feature::

    appfeature = app.enable_feature(<feature_id_or_name>)

Remove a Feature::

    appfeature = app.disable_feature(<feature_id_or_name>)

App Transfers
~~~~~~~~~~~~~

List all Transfers::

    transferlist = app.transfers()
    transferlist = app.transfers(order_by='id', limit=10)

Create a Transfer::

    transfer = app.create_transfer(id=<user_id>)
    transfer = app.create_transfer(email=<valid_email>)

Delete a Transfer::

    deletedtransfer = app.delete_transfer(<transfer_id>)
    deletedtransfer = transfer.delete()

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

Get a list of domains configured for this app::
    
    domainlist = app.domains(order_by='id')

Add a domain to this app::

    domain = app.add_domain('domain_hostname')

Remove a domain from an app::

    domain = app.remove_domain('domain_hostname')

Dynos & Process Formations
~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynos
_______

Dynos represent all your running dyno processes. Use dynos to investigate whats running on your app.
Use Dynos to create one off processes/run commands.

**You don't "scale" dyno Processes. You "scale" Formation Processes. See Formations section Below**

Get a list of running dynos::

    dynolist = app.dynos()
    dynolist = app.dynos(order_by='id')

Kill a dyno::

    app.kill_dyno(<dyno_id_or_name>)
    app.dynos['run.1'].kill()
    dyno.kill()

**Restarting your dynos is achieved by killing existing dynos, and allowing heroku to auto start them. A Handy wrapper for this proceses has been provided below.**

*N.B. This will only restart Formation processes, it will not kill off other processes.*

Restart a Dyno::

    #a simple wrapper around dyno.kill() with run protection so won't kill any proc of type='run' e.g. 'run.1'
    dyno.restart()

Restart all your app's Formation configured Dyno's::

    app.restart()

Run a command without attaching to it. e.g. start a command and return the dyno object representing the command::

    dyno = app.run_command_detached('fab -l', size=1)

Run a command and attach to it, returning the commands output as a string::

    #printout  is used to control if the task should also print to STDOUT - useful for long running processes
    #size = is the processes dyno size 1X(default), 2X, 3X etc...
    output = app.run_command('fab -l', size=1, printout=True)
    print output

Formations
_________

Formations represent the dynos that you have configured in your Procfile - whether they are running or not.
Use Formations to scale dynos up and down

Get a list of your configured Processes::

    proclist = app.process_formation()
    proclist = app.process_formation(order_by='id')
    proc = app.process_formation()['web']
    proc = heroku_conn.apps()['myapp'].process_formation()['web']

Scale your Procfile processes::

    app.process_formation()['web'].scale(2) # run 2 dynos
    app.process_formation()['web'].scale(0) # don't run any dynos
        
Resize your Procfile Processes::

    app.process_formation()['web'].resize(2) # for 2X
    app.process_formation()['web'].resize(1) # for 1X


Log Drains
~~~~~~~~~~

List all active logdrains::

    logdrainlist = app.logdrains()
    logdrainlist = app.logdrains(order_by='id')

Create a logdrain::

    loggdrain = app.create_logdrain(<url>)

Remove a logdrain::

    delete_logdrain - app.remove_logdrain(<id_or_url>)



Log Sessions
~~~~~~~~~~~~

Access the logs::

    log = app.get_log()
    log = app.get_log(lines=100)
    print app.get_log(dyno='web.1', lines=2, source='app')
    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from down to created
    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from created to starting


You can even stream the tail::

    #accepts the same params as above - lines|dyno|source
    for line in app.stream_log(lines=1):
         print line

    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from down to created
    2011-12-21T22:53:47+00:00 heroku[web.1]: State changed from created to starting

Maintenance Mode
~~~~~~~~~~~~~~~~

Enable Maintenance Mode::

    app.enable_maintenance_mode()

Disable Maintenance Mode::

    app.disable_maintenance_mode()

OAuth
~~~~~

**Not Implemented Yet**

Release
~~~~~~~

List all releases::

    releaselist = app.releases()
    releaselist = app.releases(order_by='seq')

release information::

    for release in app.releases():
        print "{0}-{1} released by {2} on {3}".format(release.id, release.description, release.user.name, release.created_at)

Rollbck to a release::

    app.rollback("v{0}".format(release.version))
    app.rollback("v108")

Rename App
~~~~~~~~~~

Rename App::

    app.rename('Carrot-kettle-teapot-1898')

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
