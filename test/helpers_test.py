import py.test
from heroku.helpers import *


def test_is_string():
    assert is_string('abc')
    assert is_string('1')
    assert is_string(str(123))
    assert not is_string(123)
    assert not is_string(['a', 'b', 'c'])
    assert not is_string(('a', 'b', 'c'))
    assert not is_string({'a': '1', 'b': '2', 'c': '3'})
    assert not is_string(True)


def test_is_collection():
    assert is_collection([])
    assert is_collection(())
    assert is_collection({})
    assert is_collection(['a', 'b', 'c'])
    assert is_collection(('a', 'b', 'c'))
    assert is_collection({'a': '1', 'b': '2', 'c': '3'})
    assert is_collection(list('heroku'))
    assert not is_collection('heroku')
    assert not is_collection(2)
    assert not is_collection(True)


