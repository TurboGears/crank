# encoding: utf-8
import pytest
from crank.restdispatcher import RestDispatcher
from crank.objectdispatcher import ObjectDispatcher
from crank.dispatchstate import DispatchState
from webob.exc import HTTPBadRequest, HTTPNotFound, HTTPMethodNotAllowed



class MockRequest(object):

    def __init__(self, path, method='GET', params=None):
        self.path_info = path
        self.params = params
        if params is None:
            self.params = {}
        self.method = method

class MockDispatcher(RestDispatcher):

    def post(self):
        pass

    def put(self):
        pass

    def post_delete(self):
        pass

    def get_delete(self):
        pass

    def get_one(self, mock_id):
        pass

    def get_all(self):
        pass

    def other(self):
        pass

class MockEmbeddedRestDispatcherWithArgs(RestDispatcher):

    def get_one(self, mock_id):
        pass
    def post(self, mock_id):
        pass
    def put(self, mock_id):
        pass
    def delete(self, mock_id):
        pass

class MockDispatcherWithArgs(RestDispatcher):

    def post(self, arg1, **kw):
        pass
    def other(self, *args):
        pass
    sub = MockEmbeddedRestDispatcherWithArgs()


class MockDispatcherWithVarArgs(RestDispatcher):
    def get_one(self, *crazy_args):
        pass
    sub = MockDispatcher()


class MockEmbeddedRestDispatcher(RestDispatcher):
    def get_one(self, mock_id):
        pass
    sub = MockDispatcher()


class MockSimpleDispatcher(RestDispatcher):

    def get(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass

class MockMinimalRestDispatcher(RestDispatcher):
    def get_one(self):
        pass

class MockError(Exception):pass
class MockRestDispatcherWithSecurity(RestDispatcher):
    def _check_security(self):
        raise MockError

    def get_one(self, *args):
        pass

class MockRestDispatcherWithNestedSecurity(RestDispatcher):
    withsec = MockRestDispatcherWithSecurity()

    def get_all(self, *args):
        pass

class MockDispatcherWithLookupOnSecurity(ObjectDispatcher):
    def _lookup(self, *args):
        if 'direct' in args:
            return MockRestDispatcherWithSecurity(), args[1:]
        if 'nested' in args:
            return MockRestDispatcherWithNestedSecurity(), args[1:]

class TestDispatcher:

    def setup_method(self, method):
        self.dispatcher = MockDispatcher()

    def test_create(self):
        pass

    def test_get_all(self):
        req = MockRequest('/')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_all'

    def test_get_one(self):
        req = MockRequest('/asdf')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_one'
        assert state.params == {}, state.params
        assert state.remainder == ['asdf'], state.remainder

    def test_post(self):
        req = MockRequest('/', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post'

    def test_post_delete(self):
        req = MockRequest('/', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post_delete'

    def test_post_delete_hacky(self):
        req = MockRequest('/', params={'_method':'delete'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post_delete'

    def test_get_delete(self):
        req = MockRequest('/delete', method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_delete'

    def test_delete_hack_bad_get(self):
        req = MockRequest('/', params={'_method':'delete'}, method='get')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPMethodNotAllowed):
            state = state.resolve()

    def test_put_hack_bad_get(self):
        req = MockRequest('/', params={'_method':'put'}, method='get')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPMethodNotAllowed):
            state = state.resolve()

    def test_put(self):
        req = MockRequest('/', params={'_method':'put'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'put', state.method

    def test_put(self):
        req = MockRequest('/', method='put')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'put', state.method

    def test_other_method(self):
        req = MockRequest('/other')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'other', state.method

class TestSimpleDispatcher:

    def setup_method(self, method):
        self.dispatcher = MockSimpleDispatcher()

    def test_get(self):
        req = MockRequest('/')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get'

    def test_post(self):
        req = MockRequest('/', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post'

    def test_delete(self):
        req = MockRequest('/', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'delete'

    def test_delete_hacky(self):
        req = MockRequest('/', params={'_method':'delete'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'delete'

class TestEmbeddedRestDispatcher:

    def setup_method(self, method):
        self.dispatcher = MockEmbeddedRestDispatcher()

    def test_create(self):
        pass

    def test_delete_hacky(self):
        req = MockRequest('/asdf/sub', params={'_method':'delete'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post_delete', state.method
        assert state.controller.__class__.__name__ == 'MockDispatcher', state.controller
        assert state.params == {}, state.params

class TestMinimalRestDispatcher:

    def setup_method(self, method):
        self.dispatcher = MockMinimalRestDispatcher()

    def test_create(self):
        pass

    def test_get_all_fallback_on_get_one(self):
        req = MockRequest('/')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_one'

class TestDispatcherWithArgs:

    def setup_method(self, method):
        self.dispatcher = MockDispatcherWithArgs()

    def test_create(self):
        pass

    def test_post(self):
        req = MockRequest('/asdf', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post'

    def test_put(self):
        req = MockRequest('/sub/asdf', method='put')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'put', state.method

    def test_delete(self):
        req = MockRequest('/sub/asdf', method='delete')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'delete', state.method

    def test_other(self):
        req = MockRequest('/other', method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'other'

    def test_other_with_get_method(self):
        req = MockRequest('/other/something', params={'_method':'get'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'other', state.method

    def test_post_bad(self):
        req = MockRequest('/aaa/aaa', method='post')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPBadRequest):
            state = state.resolve()

    def test_other_delete_bad(self):
        req = MockRequest('/other/asdf', method='delete')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPMethodNotAllowed):
            state = state.resolve()

    def test_other_delete_not_found(self):
        req = MockRequest('/not_found', method='delete')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPNotFound):
            state = state.resolve()

    def test_sub_get_one(self):
        req = MockRequest('/sub/mid', method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_one'


class TestDispatcherWithVarArgs:

    def setup_method(self, method):
        self.dispatcher = MockDispatcherWithVarArgs()

    def test_create(self):
        pass

    def test_delete(self):
        req = MockRequest('/asdf1/asdf2/asdf3/asdf4/sub')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_all', state.method

class MockCustomMethodDispatcher(RestDispatcher):

    _custom_actions = ['custom']

    def get_custom(self):
        pass

    def post_custom(self):
        pass

class TestCustomMethodDispatcher:

    def setup_method(self, method):
        self.dispatcher = MockCustomMethodDispatcher()

    def test_create(self):
        pass

    def test_post(self):
        req = MockRequest('/', method='custom')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post_custom', state.method

    def test_post_hacky(self):
        req = MockRequest('/', params={'_method':'custom'}, method='post')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'post_custom', state.method

    def test_get_hacky(self):
        req = MockRequest('/', params={'_method':'custom'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_custom', state.method

    def test_get_url(self):
        req = MockRequest('/custom')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_custom', state.method

    def test_get_fail(self):
        req = MockRequest('/not_found', params={'_method':'custom'}, method='get')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPNotFound):
            state = state.resolve()

class SubCustomMethodDispatcher(MockDispatcher):

    sub = MockCustomMethodDispatcher()

class TestSubCustomMethodDispatcher:

    def setup_method(self, method):
        self.dispatcher = SubCustomMethodDispatcher()

    def test_create(self):
        pass

    def test_get_url(self):
        req = MockRequest('/sub', params={'_method':'custom'}, method='get')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.action.__name__ == 'get_custom', state.method

class SubNoGet(RestDispatcher):
    pass

class OtherSubCustomMethodDispatcher(MockDispatcher):
    sub = SubNoGet()

class TestSubNoGetDispatcher:

    def setup_method(self, method):
        self.dispatcher = OtherSubCustomMethodDispatcher()

    def test_create(self):
        pass

    def test_get_not_found(self):
        req = MockRequest('/sub', method='get')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPNotFound):
            state = state.resolve()

class TestEmptyDispatcher:
    def setup_method(self, method):
        self.dispatcher = SubNoGet()

    def test_create(self):
        pass

    def test_get_not_found(self):
        req = MockRequest('/sub', method='get')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(HTTPNotFound):
            state = state.resolve()

class TestRestWithSecurity:
    def setup_method(self, method):
        self.dispatcher = MockDispatcherWithLookupOnSecurity()

    def test_check_security_with_lookup(self):
        req = MockRequest('/direct/a')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(MockError):
            state = state.resolve()

    def test_check_security_with_nested_lookup(self):
        req = MockRequest('/nested/withsec/a')
        state = DispatchState(req, self.dispatcher)
        with pytest.raises(MockError):
            state = state.resolve()

class TestRestWithLookup:
    class RootController(ObjectDispatcher):
        class rest(RestDispatcher):
            class sub(ObjectDispatcher):
                def method(self):
                    pass
            sub = sub()

            def get(self, itemid):
                return str(itemid)

            def _lookup(self, *args, **kw):
                return self.sub, args[1:]
        rest = rest()

    def setup_method(self, method):
        self.dispatcher = self.RootController()

    def test_rest_with_lookup(self):
        req = MockRequest('/rest/somethingelse/method')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'sub', state.controller
        assert state.action.__name__ == 'method', state.method

    def test_rest_lookup_doesnt_mess_with_get(self):
        req = MockRequest('/rest/25')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'rest', state.controller
        assert state.action.__name__ == 'get', state.method

    def test_rest_lookup_doesnt_mess_with_subcontroller(self):
        req = MockRequest('/rest/sub/method')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'sub', state.controller
        assert state.action.__name__ == 'method', state.method

class TestRestCheckSecurity:
    class RootController(ObjectDispatcher):
        class rest(RestDispatcher):
            def _check_security(self):
                self.trace_security_visits.append(True)
                return True

            def get(self, itemid):
                return str(itemid)

        rest = rest()

    def setup_method(self, method):
        self.security_tracing = []
        self.dispatcher = self.RootController()
        self.dispatcher.rest.trace_security_visits = self.security_tracing

    def test_rest_security_check_only_once(self):
        req = MockRequest('/rest/25')
        state = DispatchState(req, self.dispatcher)
        state = state.resolve()
        assert state.controller.__class__.__name__ == 'rest', state.controller
        assert state.action.__name__ == 'get', state.method
        assert len(self.security_tracing) == 1, self.security_tracing


class NestedBodyMethodDispatcher(RestDispatcher):
    def post(self):
        pass

    def put(self):
        pass

    def patch(self):
        pass


class BodyMethodDispatcher(RestDispatcher):
    nested = NestedBodyMethodDispatcher()

    def post(self, required, optional=None):
        pass

    def put(self, required, optional=None):
        pass

    def patch(self, required, optional=None):
        pass

    def get_one(self, required):
        pass

    def delete(self, required):
        pass

    def custom(self, required):
        pass

    def direct(self, required):
        pass


class BodyMethodDefaultFallbackDispatcher(BodyMethodDispatcher):
    def _default(self, *args, **kwargs):
        pass


class BodyMethodLookupTarget(ObjectDispatcher):
    def index(self):
        pass


class BodyMethodLookupFallbackDispatcher(BodyMethodDispatcher):
    target = BodyMethodLookupTarget()

    def _lookup(self, *args, **kwargs):
        return self.target, args


class AbsentBodyMethodDefaultFallbackDispatcher(RestDispatcher):
    def _default(self, *args, **kwargs):
        pass


class AbsentBodyMethodLookupFallbackDispatcher(RestDispatcher):
    target = BodyMethodLookupTarget()

    def _lookup(self, *args, **kwargs):
        return self.target, args


class MixedBodyMethodDispatcher(RestDispatcher):
    def post(self, first, second):
        pass

    def put(self, first, second):
        pass

    def patch(self, first, second):
        pass


class PostVerbFallbackDispatcher(RestDispatcher):
    def post_patch(self):
        pass

    def post_custom(self):
        pass

    def _default(self, *args, **kwargs):
        pass


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
def test_body_method_missing_required_argument_is_bad_request(method):
    request = MockRequest('/', method=method)

    with pytest.raises(HTTPBadRequest):
        DispatchState(request, BodyMethodDispatcher()).resolve()


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
def test_body_method_mixed_path_and_keyword_missing_arg_is_bad_request(method):
    request = MockRequest('/from-path', method=method, params={'first': 'from-param'})

    with pytest.raises(HTTPBadRequest):
        DispatchState(request, MixedBodyMethodDispatcher()).resolve()


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
@pytest.mark.parametrize(
    'path, params, remainder',
    (
        ('/from-path', {}, ['from-path']),
        ('/', {'required': 'from-param'}, []),
    ),
)
def test_body_method_accepts_required_path_or_keyword_argument(method, path, params, remainder):
    state = DispatchState(MockRequest(path, method=method, params=params),
                          BodyMethodDispatcher()).resolve()

    assert state.action.__name__ == method.lower()
    assert state.remainder == remainder


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
@pytest.mark.parametrize(
    'path, params',
    (
        ('/one/two/three', {}),
        ('/', {'required': 'value', 'unexpected': 'value'}),
        ('/', {'unexpected': 'value'}),
    ),
)
@pytest.mark.parametrize(
    'dispatcher',
    (BodyMethodDefaultFallbackDispatcher, BodyMethodLookupFallbackDispatcher),
)
def test_body_method_route_mismatch_is_bad_request(method, path, params, dispatcher):
    request = MockRequest(path, method=method, params=params)

    with pytest.raises(HTTPBadRequest):
        DispatchState(request, dispatcher()).resolve()


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
@pytest.mark.parametrize(
    'dispatcher, action',
    (
        (AbsentBodyMethodDefaultFallbackDispatcher, '_default'),
        (AbsentBodyMethodLookupFallbackDispatcher, 'index'),
    ),
)
def test_absent_body_method_uses_fallback(method, dispatcher, action):
    state = DispatchState(MockRequest('/', method=method), dispatcher()).resolve()

    assert state.action.__name__ == action


@pytest.mark.parametrize('method', ('GET', 'DELETE', 'CUSTOM'))
def test_non_body_method_missing_required_argument_is_not_found(method):
    request = MockRequest('/', method=method)

    with pytest.raises(HTTPNotFound):
        DispatchState(request, BodyMethodDispatcher()).resolve()


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
def test_body_method_direct_exposed_path_has_precedence(method):
    state = DispatchState(MockRequest('/direct', method=method),
                          BodyMethodDispatcher()).resolve()

    assert state.action.__name__ == 'direct'
    assert state.remainder == []


@pytest.mark.parametrize('method', ('POST', 'PUT', 'PATCH'))
def test_body_method_nested_controller_has_precedence(method):
    state = DispatchState(MockRequest('/nested', method=method),
                          BodyMethodDispatcher()).resolve()

    assert state.controller.__class__ is NestedBodyMethodDispatcher
    assert state.action.__name__ == method.lower()


@pytest.mark.parametrize(
    'method, action',
    (
        ('PATCH', '_default'),
        ('CUSTOM', 'post_custom'),
    ),
)
def test_patch_skips_post_patch_but_custom_verbs_keep_post_fallback(method, action):
    state = DispatchState(MockRequest('/', method=method),
                          PostVerbFallbackDispatcher()).resolve()

    assert state.action.__name__ == action
