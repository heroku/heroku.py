Heroku.py
=========

This is an awesome Python wrapper for the Heroku API. The Heroku REST API
allows Heroku users to manage their accounts, applications, addons, and
other aspects related to Heroku. It allows you to easily utilize the Heroku
platform from your applications.


Usage
-----

Login with your API Key ( `available here <https://api.heroku.com/account>`_ )::

    >>> from heroku import from_key
    >>> heroku = from_key('YOUR_API_KEY')


Installation
------------

To install ``heroku.py``, simply:

To install requests, simply::

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