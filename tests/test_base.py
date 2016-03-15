import pytest

from pystachio.base import Environment, Object
from pystachio.basic import Integer
from pystachio.container import List
from pystachio.naming import Namable, Ref


def dtd(d):
  return dict((Ref.from_address(key), str(val)) for key, val in d.items())

def ref(address):
  return Ref.from_address(address)


def test_environment_constructors():
  oe = Environment(a = 1, b = 2)
  assert oe._table == dtd({'a': 1, 'b': 2})

  oe = Environment({'a': 1, 'b': 2})
  assert oe._table == dtd({'a': 1, 'b': 2})

  oe = Environment({'a': 1}, b = 2)
  assert oe._table == dtd({'a': 1, 'b': 2})

  oe = Environment({'a': 1}, a = 2)
  assert oe._table == dtd({'a': 2}), "last update should win"

  oe = Environment({'b': 1}, a = 2)
  assert oe._table == dtd({'a': 2, 'b': 1})

  oe = Environment(oe, a = 3)
  assert oe._table == dtd({'a': 3, 'b': 1})

  bad_values = [None, 3, 'a', type, ()]
  for value in bad_values:
    with pytest.raises(ValueError):
      Environment(value)
  bad_values = [None, type, ()]
  for value in bad_values:
    with pytest.raises(ValueError):
      Environment(foo = value)


def test_environment_find():
  oe1 = Environment(a = { 'b': 1 })
  oe2 = Environment(a = { 'b': { 'c': List(Integer)([1,2,3]) } } )
  oe = Environment(oe1, oe2)
  assert oe.find(ref('a.b')) == '1'
  assert oe.find(ref('a.b.c[0]')) == Integer(1)
  assert oe.find(ref('a.b.c[1]')) == Integer(2)
  assert oe.find(ref('a.b.c[2]')) == Integer(3)

  missing_refs = [ref('b'), ref('b.c'), ref('a.c'), ref('a.b.c[3]')]
  for r in missing_refs:
    with pytest.raises(Namable.NotFound):
      oe.find(r)

  oe = Environment(a = { 'b': { 'c': 5 } } )
  assert oe.find(ref('a.b.c')) == '5'


def test_environment_merge():
  oe1 = Environment(a = 1)
  oe2 = Environment(b = 2)
  assert Environment(oe1, oe2)._table == {
    ref('a'): '1',
    ref('b'): '2'
  }

  oe1 = Environment(a = 1, b = 2)
  oe2 = Environment(a = 1, b = {'c': 2})
  assert Environment(oe1, oe2)._table == {
    ref('a'): '1',
    ref('b'): '2',
    ref('b.c'): '2'
  }

  oe1 = Environment(a = 1, b = 2)
  oe2 = Environment(a = 1, b = {'c': 2})
  assert Environment(oe2, oe1)._table == {
    ref('a'): '1',
    ref('b'): '2',
    ref('b.c'): '2'
  }

  oe1 = Environment(a = { 'b': 1 })
  oe2 = Environment(a = { 'c': 2 })
  assert Environment(oe1, oe2)._table == {
    ref('a.b'): '1',
    ref('a.c'): '2'
  }
  assert Environment(oe2, oe1)._table == {
    ref('a.b'): '1',
    ref('a.c'): '2'
  }


def test_environment_bad_values():
  bad_values = [None, type, object()]
  for val in bad_values:
    with pytest.raises(ValueError):
      Environment(a = val)


def test_object_unimplementeds():
  o = Object()
  with pytest.raises(NotImplementedError):
    Object.checker(o)
  with pytest.raises(NotImplementedError):
    o.get()
  with pytest.raises(NotImplementedError):
    oi = o.interpolate()
