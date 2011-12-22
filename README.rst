Heroku.py
=========

This is an awesome Python wrapper for the Heroku API. The Heroku REST API
allows Heroku users to manage their accounts, applications, addons, and
other aspects related to Heroku. It allows you to easily utilize the Heroku
platform from your applications.


Usage
-----

Login with your password::

    import heroku
    cloud = heroku.from_pass('kenneth@heroku.com', 'xxxxxxx')

Or your API Key (`available here <https://api.heroku.com/account>`_)::

    cloud = heroku.from_key('YOUR_API_KEY')

Interact with your applications::

    >>> cloud.apps
    [<app 'sharp-night-7758'>, <app 'empty-spring-4049'>, ...]

    >>> app = cloud.apps['sharp-night-7758']


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

    >>> for line in app.logs(trail=True):
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

    >>> app.delete()
    True

And much more. Detailed docs forthcoming.


Installation
------------

To install ``heroku.py``, simply::

    $ pip install heroku

Or, if you absolutely must::

    $ easy_install heroku

But, you `really shouldn't do that <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.


License
-------

Copyright (c) 2011 Heroku, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.