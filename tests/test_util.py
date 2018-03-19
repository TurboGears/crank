# encoding: utf-8
from crank.util import *
from crank.util import _PY2
import functools

if _PY2:
    def u(s): return s.decode('utf-8')
else:
    def u(s): return s

def mock_f(self, a, b, c=None, d=50, *args, **kw):
    pass

def mock_f2(self, a, b):
    pass

def decorator(f):
    @functools.wraps(f)
    def f_(*args, **kwargs):
        return f(*args, **kwargs)
    if not hasattr(f_, '__wrapped__'):
        # Not all python versions update it
        f_.__wrapped__ = f
    return f_

deco_mock_f = decorator(mock_f)

class mock_c(object):
    def mock_f(self, a, b):
        pass

def test_get_argspec_first_call():
    argspec = get_argspec(mock_f)
    assert argspec == (['a', 'b', 'c', 'd'], 'args', 'kw', (None, 50)), argspec
    deco_argspec = get_argspec(deco_mock_f)
    assert argspec == deco_argspec, deco_argspec

def test_get_argspec_cached():
    argspec = get_argspec(mock_f)
    assert argspec == (['a', 'b', 'c', 'd'], 'args', 'kw', (None, 50)), argspec
    deco_argspec = get_argspec(deco_mock_f)
    assert argspec == deco_argspec, deco_argspec

def test_get_params_with_argspec():
    params = get_params_with_argspec(mock_f, {'a':1, 'c':2}, [3])
    assert params == {'a': 3, 'c': 2}, params

def test_get_params_with_argspec_class():
    params = get_params_with_argspec(mock_c().mock_f, {'a':1, 'c':2}, [3])
    assert params == {'a': 3, 'c': 2}, params


class TestFlattenArguments(object):
    def test_flatten_arguments(self):
        remainder, params = flatten_arguments(mock_f, {'a':1, 'b':2}, [3])
        assert params == {}, params
        assert remainder == (1, 2, None, 50), repr(remainder)

    def test_flatten_arguments_optional_positionals(self):
        remainder, params = flatten_arguments(mock_f, {'c':45}, [3, 3, 4])
        assert params == {}, params
        assert remainder == (3, 3, 45, 50), repr(remainder)

    def test_flatten_arguments_keep_extra_keyword(self):
        remainder, params = flatten_arguments(mock_f, {'c': 45, 'z': 45}, [3, 3, 4])
        assert params == {'z': 45}, params
        assert remainder == (3, 3, 45, 50), repr(remainder)

    def test_flatten_arguments_keep_extra_positional(self):
        remainder, params = flatten_arguments(mock_f, {'c': 45, 'z': 45}, [3, 3, 4, 50, 72])
        assert params == {'z': 45}, params
        assert remainder == (3, 3, 45, 50, 72), repr(remainder)

    def test_flatten_arguments_none_remainder(self):
        remainder, params = flatten_arguments(mock_f, {'a':1, 'b':2}, None)
        assert params == {}, params
        assert remainder == (1, 2, None, 50), repr(remainder)

    def test_flatten_arguments_none_param(self):
        remainder, params = flatten_arguments(mock_f, {'b': None}, [3, 3])
        assert params == {}, params
        assert remainder == (3, None, None, 50), repr(remainder)

    def test_flatten_arguments_in_remainder(self):
        remainder, params = flatten_arguments(mock_f2, {'b':1}, ['a'])
        assert params == {}, params
        assert remainder == ('a', 1,), repr(remainder)

    def test_flatten_arguments_no_conditionals(self):
        remainder, params = flatten_arguments(mock_f2, {'a':1, 'b':2}, ['a'])
        assert params == {}, params
        assert remainder == (1,2), repr(remainder)

    def test_flatten_arguments_req_var_in_params(self):
        remainder, params = flatten_arguments(mock_f2, {'a':1, 'b':2}, ['a'])
        assert params == {}, params
        assert remainder == (1, 2), repr(remainder)

    def test_flatten_arguments_avoid_creating_duplicate_parameters(self):
        remainder, params = flatten_arguments(mock_f, {'a':1, 'b':2, 'c':3}, ['a', 'b'])
        assert params == {}, params
        assert remainder == (1, 2, 3, 50), repr(remainder)

    def test_flatten_arguments_avoid_duplicate_params(self):
        remainder, params = flatten_arguments(mock_f2, {'a':1, 'b':2}, ['a', 'b'])
        assert params == {}, params
        assert remainder == (1, 2), remainder

    def test_flatten_arguments_all_positional_with_unexpected_arg(self):
        remainder, params = flatten_arguments(mock_f2, {}, ['a', 'b', 'c'])
        assert params == {}, params
        assert remainder == ('a', 'b'), remainder

    def test_flatten_arguments_all_positional(self):
        remainder, params = flatten_arguments(mock_f2, {}, ['a', 'b'])
        assert params == {}, params
        assert remainder == ('a', 'b'), remainder

    def test_flatten_arguments_all_positional_unexpected_but_varargs(self):
        remainder, params = flatten_arguments(mock_f, {}, ['a', 'b', 'c', 'd', 'e'])
        assert params == {}, params
        assert remainder == ('a', 'b', 'c', 'd', 'e'), remainder

    def test_flatten_arguments_missing_first_argument(self):
        try:
            remainder, params = flatten_arguments(mock_f2, {'b': 2}, [])
        except TypeError as e:
            assert 'missing "a" required argument' in str(e)
        else:
            assert False, 'should have triggered missed argument'

    def test_flatten_arguments_missing_last_argument(self):
        try:
            remainder, params = flatten_arguments(mock_f2, {'a': 1}, [])
        except TypeError as e:
            assert 'missing "b" required argument' in str(e)
        else:
            assert False, 'should have triggered missed argument'


def test_remove_argspec_params_from_params():
    params, remainder = remove_argspec_params_from_params(mock_f, {'a':1, 'b':2}, [3])
    assert params == {}, params
    assert remainder == (1, 2), repr(remainder)

def test_remove_argspec_params_from_params_remove_optional_positionals():
    params, remainder = remove_argspec_params_from_params(mock_f, {'c':45}, [3, 3, 4])
    assert params == {}, params
    assert remainder == (3, 3, 45), repr(remainder)

def test_remove_argspec_params_from_params_none_remainder():
    params, remainder = remove_argspec_params_from_params(mock_f, {'a':1, 'b':2}, None)
    assert params == {'a': 1, 'b': 2}, params
    assert remainder == None, repr(remainder)

def test_remove_argspec_params_from_params_none_param():
    params, remainder = remove_argspec_params_from_params(mock_f, {'b':None}, [3, 3])
    assert params == {}, params
    assert remainder == (3, None), repr(remainder)

def test_remove_argspec_params_from_params_in_remainder():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'b':1}, ['a'])
    assert params == {}, params
    assert remainder == ('a', 1,), repr(remainder)

def test_remove_argspec_params_from_params_no_conditionals():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'a':1, 'b':2}, ['a'])
    assert params == {}, params
    assert remainder == (1,2), repr(remainder)

def test_remove_argspec_params_from_params_req_var_in_params():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'a':1, 'b':2}, ['a'])
    assert params == {}, params
    assert remainder == (1, 2), repr(remainder)

def test_remove_argspec_params_from_params_avoid_creating_duplicate_parameters():
    params, remainder = remove_argspec_params_from_params(mock_f, {'a':1, 'b':2, 'c':3}, ['a', 'b'])
    assert params == {'c': 3}, params
    assert remainder == (1, 2), repr(remainder)

def test_remove_argspec_params_from_params_avoid_duplicate_params():
    params, remainder = remove_argspec_params_from_params(mock_f2, {'a':1, 'b':2}, ['a', 'b'])


def test_method_matches_args_no_remainder():
    params = {'a':1, 'b':2, 'c':3}
    remainder = []
    r = method_matches_args(mock_f, params, remainder)
    assert r

def test_method_matches_args_no_lax_params():
    params = {'a':1, 'b':2, 'c':3, 'x':4}
    remainder = []
    r = method_matches_args(mock_f2, params, remainder, False)
    assert not(r)

def test_method_matches_args_fails_no_remainder():
    params = {'a':1, 'x':3}
    remainder = []
    r = method_matches_args(mock_f, params, remainder)
    assert not(r)

def test_method_matches_args_no_params():
    params = {}
    remainder = [1, 2]
    r = method_matches_args(mock_f, params, remainder)
    assert r

def test_method_matches_args_fails_no_params():
    params = {}
    remainder = [2]
    r = method_matches_args(mock_f, params, remainder)
    assert not(r)

def test_method_matches_args_fails_no_params():
    params = {}
    remainder = [2]
    r = method_matches_args(mock_f2, params, remainder)
    assert not(r)

def test_method_matches_args_fails_more_remainder_than_argspec():
    params = {}
    remainder = [2, 3, 4, 5]
    r = method_matches_args(mock_f2, params, remainder)
    assert not(r)

def mock_f3(self, a, b, c=None, d=50):
    pass

def test_method_matches_args_with_default_values():
    params = {'a':1, 'b':2, 'c':3, 'd':4}
    remainder = []
    r = method_matches_args(mock_f3, params, remainder)
    assert r

def assert_path(instance, expected, kind=list):
    assert kind(instance.path) == expected, (kind(instance.path), expected)

def test_path_path():
    assert Path(Path('/foo')) == ['', 'foo']

def test_path_list():
    class MockOb(object):
        path = Path()
    
    cases = [
            ('/', ['', '']),
            ('/foo', ['', 'foo']),
            ('/foo/bar', ['', 'foo', 'bar']),
            ('/foo/bar/', ['', 'foo', 'bar', '']),
            ('/foo//bar/', ['', 'foo', '', 'bar', '']),
            (('foo', ), ['foo']),
            (('foo', 'bar'), ['foo', 'bar'])
        ]
    
    for case, expected in cases:
        instance = MockOb()
        instance.path = case
        
        yield assert_path, instance, expected

def test_path_str():
    class MockOb(object):
        path = Path()
    
    cases = [
            ('/', "/"),
            ('/foo', '/foo'),
            ('/foo/bar', '/foo/bar'),
            ('/foo/bar/', '/foo/bar/'),
            ('/foo//bar/', '/foo//bar/'),
            (('foo', ), 'foo'),
            (('foo', 'bar'), 'foo/bar')
        ]
    
    for case, expected in cases:
        instance = MockOb()
        instance.path = case
        
        yield assert_path, instance, expected, str
    
    instance = MockOb()
    instance.path = '/foo/bar'
    yield assert_path, instance, """<Path ['', 'foo', 'bar']>""", repr

def test_path_unicode():
    class MockOb(object):
        path = Path()
    
    cases = [
            ('/', "/"),
            (u('/©'), u('/©')),
            (u('/©/™'), u('/©/™')),
            (u('/©/™/'), u('/©/™/')),
            ((u('¡'), ), u('¡')),
            (('foo', u('¡')), u('foo/¡'))
        ]
    
    for case, expected in cases:
        instance = MockOb()
        instance.path = case

        if _PY2:
            yield assert_path, instance, expected, unicode
        else:
            yield assert_path, instance, expected, str

def test_path_slicing():
    class MockOb(object):
        path = Path()
    
    instance = MockOb()
    
    instance.path = '/foo/bar/baz'
    
    assert str(instance.path[1:]) == 'foo/bar/baz'
    assert str(instance.path[2:]) == 'bar/baz'
    assert str(instance.path[0:2]) == '/foo'
    assert str(instance.path[::2]) == '/bar'

def test_path_comparison():
    assert Path('/foo') == ('', 'foo'), 'tuple comparison'
    assert Path('/foo') == ['', 'foo'], 'list comparison'
    assert Path('/foo') == '/foo', 'string comparison'
    assert Path(u('/föö')) == u('/föö'), 'string comparison'

def test_path_translation():
    translated = default_path_translator('a.b')
    assert translated == 'a_b', translated

    translated = default_path_translator(u('f.ö.ö'))
    assert translated == u('f_ö_ö'), translated
