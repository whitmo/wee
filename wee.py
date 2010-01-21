from webob import Request, Response
from webob import exc
import functools
import re
import sys


def handle_request(environ, start_response, module=None, request_class=Request, response_class=Response):
    """The main handler. Dispatches to the user's code."""
    try:
        request = request_class(environ)
        verb = VERB.get(request.method)
        response = verb.dispatch(request, module)
        if response is None:
            raise exc.HTTPNotFound()
    except Exception, e:
        return e(environ, start_response)
    
    if isinstance(response, basestring):
        response = response_class(response)
    
    return response(environ, start_response)


def make_simple_app(module=None, which_r=None):
    """
    Module name may be specified, otherwhise we stack jump and use the
    one where this function is called.
    
    If which_r is set to 'wz', wee will use the werkzeug request and
    response objects
    """
    if module is None:
        module = sys._getframe(1).f_globals['__name__']
    if which_r == 'wz':
        from werkzeug import Request, Response
    else:
        global Request, Response
    return functools.partial(handle_request, module=module, request_class=Request, response_class=Response)


def handle_error(exception, request):
    """
    If an exception is thrown, deal with it and present an error page.
    """
    if isinstance(exception, exc.WSGIHTTPException):
        status = getattr(exception, 'code', 404)
    
    if status in exc.status_map:
        return exc.status_map[status](request, exception)
    
    return exc.HTTPNotFound(request, exception)


class Verb(object):
    handlers = dict()
    def __init__(self, url):
        self.url = url
        
    def __call__(self, func):
        func._wee_verb = self
        self.add_handler(func)
        return func

    @classmethod
    def add_handler(cls, func):
        key = func.__module__, re.compile(func._wee_verb.url),
        if cls.handlers.has_key(key):
            raise ValueError("Whoah there! You can't have the same regex for more than one "\
                             "function in a single module.")
        cls.handlers[key]=func

    @classmethod
    def dispatch(cls, request, app_module):
        for key in cls.handlers:
            module, regex, = key
            if module == app_module:
                match = regex.search(request.environ['PATH_INFO'])
                if match is not None:
                    return cls.handlers[key](request, **match.groupdict())

    
class get(Verb):
    """ the get """
    handlers = dict()

class post(Verb):
    """ the post """
    handlers = dict()

class delete(Verb):
    handlers = dict()

class put(Verb):
    handlers = dict()

VERB = dict(POST=post,
            GET=get,
            PUT=put,
            DELETE=delete)
