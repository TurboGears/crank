"""
Utilities used by crank.

Copyright (c) Chrispther Perkins
MIT License
"""

import collections
import inspect
import string
import sys

__all__ = [
    'get_argspec', 'get_params_with_argspec', 'remove_argspec_params_from_params',
    'Path', 'default_path_translator'
]


_PY2 = bool(sys.version_info[0] == 2)


class _NotFound(object):
    pass


def _getargspec(func):
    if not hasattr(inspect, 'signature'):
        return inspect.getargspec(func)

    sig = inspect.signature(func)
    args = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]
    varargs = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_POSITIONAL
    ]
    varargs = varargs[0] if varargs else None
    varkw = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_KEYWORD
    ]
    varkw = varkw[0] if varkw else None
    defaults = tuple((
        p.default for p in sig.parameters.values()
        if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and p.default is not p.empty
    )) or None
    return args, varargs, varkw, defaults


_cached_argspecs = {}
def get_argspec(func):
    if _PY2:
        im_func = getattr(func, 'im_func', func)
    else:
        im_func = getattr(func, '__func__', func)

    try:
        argspec = _cached_argspecs[im_func]
    except KeyError:
        spec = _getargspec(im_func)
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
        val = params.get(var, _NotFound)
        if val is not _NotFound:
            if i < remainder_len:
                remainder[i] = val
            else:
                remainder.append(val)
            del params[var]

    # remove the optional positional variables (remainder) from the named parameters
    # until we run out of remainder, that is, avoid creating duplicate parameters
    for i, (original, var) in enumerate(zip(remainder[len(required_vars):],optional_vars)):
        if var in params:
            remainder[ len(required_vars)+i ] = params[var]
            del params[var]

    return params, tuple(remainder)


if _PY2: #pragma: no cover
    translation_dict = dict([(ord(c), unicode('_')) for c in unicode(string.punctuation)])
    translation_string = string.maketrans(string.punctuation,
                                          '_' * len(string.punctuation))
else: #pragma: no cover
    translation_dict = None
    translation_string = str.maketrans(string.punctuation,
                                       '_' * len(string.punctuation))


def default_path_translator(path_piece):
    if isinstance(path_piece, str):
        return path_piece.translate(translation_string)
    else: #pragma: no cover
        return path_piece.translate(translation_dict)


def noop_translation(path_piece):
    return path_piece


class Path(collections.deque):
    def __init__(self, value=None, separator='/'):
        self.separator = separator

        super(Path, self).__init__()

        if value is not None:
            self._assign(value)

    def _assign(self, value):
        separator = self.separator
        self.clear()

        if not _PY2: # pragma: no cover
            string_types = str
        else: # pragma: no cover
            string_types = basestring

        if isinstance(value, string_types):
            self.extend(value.split(separator))
            return

        self.extend(value)

    def __set__(self, obj, value):
        self._assign(value)

    def __str__(self):
        return str(self.separator).join(self)

    def __unicode__(self): # pragma: no cover
        #unused on PY3
        return unicode(self.separator).join(self)

    def __repr__(self):
        return "<Path %r>" % super(Path, self).__repr__()

    def __eq__(self, other):
        return type(other)(self) == other

    def __getitem__(self, i):
        try:
            return super(Path, self).__getitem__(i)

        except TypeError:
            return Path([self[i] for i in range(*i.indices(len(self)))])
