"""
Utilities used by crank.

Copyright (c) Chrispther Perkins
MIT License
"""

import collections

__all__ = [
        'odict',
        'get_argspec', 'get_params_with_argspec', 'remove_argspec_params_from_params', 'method_matches_args',
        'Path'
    ]


class odict(dict):

    def __init__(self, *args, **kw):
        self._ordering = []
        dict.__init__(self, *args, **kw)

    def __setitem__(self, key, value):
        if key in self._ordering:
            self._ordering.remove(key)
        self._ordering.append(key)
        dict.__setitem__(self, key, value)

    def keys(self):
        return self._ordering

    def clear(self):
        self._ordering = []
        dict.clear(self)

    def getitem(self, n):
        return self[self._ordering[n]]

#    def __slice__(self, a, b=-1, n=1):
#        return self.values()[a:b:n]

    def iteritems(self):
        for item in self._ordering:
            yield item, self[item]

    def items(self):
        return [i for i in self.iteritems()]

    def itervalues(self):
        for item in self._ordering:
            yield self[item]

    def values(self):
        return [i for i in self.itervalues()]

    def __delitem__(self, key):
        self._ordering.remove(key)
        dict.__delitem__(self, key)

    def pop(self):
        item = self._ordering[-1]
        del self[item]

    def __str__(self):
        return str(self.items())

from inspect import getargspec

_cached_argspecs = {}
def get_argspec(func):
    try:
        im_func = func.im_func
    except AttributeError:
        im_func = func

    try:
        argspec = _cached_argspecs[im_func]
    except KeyError:
        spec = getargspec(im_func)
        argvals = spec[3]

        # this is a work around for a crappy api choice in getargspec
        if argvals is None:
            argvals = []

        argspec = _cached_argspecs[im_func] = (spec[0][1:], spec[1], spec[2], argvals)

    return argspec

def get_params_with_argspec(func, params, remainder):
    argvars, var_args, argkws, argvals = get_argspec(func)

    if argvars and remainder:
        params = params.copy()
        remainder_len = len(remainder)
        for i, var in enumerate(argvars):
            if i >= remainder_len:
                break
            params[var] = remainder[i]
    return params

def remove_argspec_params_from_params(func, params, remainder):
    """Remove parameters from the argument list that are
       not named parameters
       Returns: params, remainder"""

    # figure out which of the vars in the argspec are required
    argvars, var_args, argkws, argvals = get_argspec(func)

    # if there are no required variables, or the remainder is none, we
    # have nothing to do
    if not argvars or not remainder:
        return params, remainder

    required_vars = argvars
    optional_vars = []
    if argvals:
        required_vars = argvars[:-len(argvals)]
        optional_vars = argvars[-len(argvals):]

    # make a copy of the params so that we don't modify the existing one
    params=params.copy()

    # replace the existing required variables with the values that come in
    # from params. these could be the parameters that come off of validation.
    remainder = list(remainder)
    remainder_len = len(remainder)
    for i, var in enumerate(required_vars):
        val = params.get(var, None)
        if i < remainder_len and val:
            remainder[i] = val
        elif val:
            remainder.append(val)
        if val:
            del params[var]

    # remove the optional positional variables (remainder) from the named parameters
    # until we run out of remainder, that is, avoid creating duplicate parameters
    for i, (original, var) in enumerate(zip(remainder[len(required_vars):],optional_vars)):
        if var in params:
            remainder[ len(required_vars)+i ] = params[var]
            del params[var]

    return params, tuple(remainder)


def method_matches_args(method, params, remainder, lax_params=False):
    """
    This method matches the params from the request along with the remainder to the
    method's function signiture.  If the two jive, it returns true.

    It is very likely that this method would go into ObjectDispatch in the future.
    """
    argvars, ovar_args, argkws, argvals = get_argspec(method)

    required_vars = argvars
    if argvals:
        required_vars = argvars[:-len(argvals)]

    params = params.copy()

    #remove the appropriate remainder quotient
    if len(remainder)<len(required_vars):
        #pull the first few off with the remainder
        required_vars = required_vars[len(remainder):]
    else:
        #there is more of a remainder than there is non optional vars
        required_vars = []

    #remove vars found in the params list
    for var in required_vars[:]:
        if var in params:
            required_vars.pop(0)
            # remove the param from the params so when we see if
            # there are params that arent in the non-required vars we
            # can evaluate properly
            del params[var]
        else:
            break;

    #remove params that have a default value
    vars_with_default = argvars[len(argvars)-len(argvals):]
    for var in vars_with_default:
        if var in params:
            del params[var]

    #make sure no params exist if keyword argumnts are missing
    if not lax_params and argkws is None and params:
        return False

    #make sure all of the non-optional-vars are there
    if not required_vars:
        #there are more args in the remainder than are available in the argspec
        if len(argvars)<len(remainder) and not ovar_args:
            return False
        return True


    return False


class Path(collections.deque):
    def __init__(self, value=None, separator='/'):
        self.separator = separator

        super(Path, self).__init__()

        if value is not None:
            self._assign(value)

    def _assign(self, value):
        separator = self.separator
        self.clear()

        if isinstance(value, (str, unicode)):
            self.extend(value.split(separator))
            return

        self.extend(value)

    def __set__(self, obj, value):
        self._assign(value)

    def __str__(self):
        return str(self.separator).join(self)

    def __unicode__(self):
        return unicode(self.separator).join(self)

    def __repr__(self):
        return "<Path %r>" % super(Path, self).__repr__()

    def __cmp__(self, other):
        return cmp(type(other)(self), other)

    def __getitem__(self, i):
        try:
            return super(Path, self).__getitem__(i)

        except TypeError:
            return Path([self[i] for i in xrange(*i.indices(len(self)))])
