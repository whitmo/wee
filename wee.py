from webob import Request, Response
from webob import exc
import functools
import re
import sys
import venusian


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
        venusian.attach(func, self.add_handler)
        return func

    @classmethod
    def add_handler(cls, scanner, name, func):
        handlers = cls.handlers
        if scanner.registry is not None:
            handlers = scanner.registry[cls.__name__.upper()]
            
        key = func.__module__, re.compile(func._wee_verb.url),
        if handlers.has_key(key):
            raise ValueError("Whoah there! You can't have the same regex for more than one "\
                             "function in a single module.")
        handlers[key]=func

    @classmethod
    def dispatch(cls, request, app_module, handlers=None):
        if handlers is None:
            handlers = cls.handlers
            
        for key in handlers:
            module, regex, = key
            if module == app_module:
                match = regex.search(request.environ['PATH_INFO'])
                if match is not None:
                    return handlers[key](request, **match.groupdict())
    

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


class DispatchRegistry(dict):

    verb = dict(POST=post,
                GET=get,
                PUT=put,
                DELETE=delete)

    def __init__(self):
        for verb in self.verb:
            self[verb]=dict()

    def __call__(self, request, app_module):
        verb = self.get(request.method)
        
        for key in verb:
            module, regex, = key
            if module == app_module:
                match = regex.search(request.environ['PATH_INFO'])
                if match is not None:
                    return verb[key](request, **match.groupdict())
    

VERB = DispatchRegistry()


# make into an object

def handle_request(environ, start_response, module=None, 
                   request_class=Request, response_class=Response, dispatch=VERB):
    """
    The main handler. Dispatches to the user's code.
    """
    request = request_class(environ)
    try:
        response = dispatch(request, module)
        if response is None:
            raise exc.HTTPNotFound()
    except exc.WSGIHTTPException, e:
        return e(environ, start_response)
    except Exception, e:
        return exc.HTTPServerError('Server Error')
    
    if isinstance(response, basestring):
        response = response_class(response)
    
    return response(environ, start_response)


def make_app(module=None, registry=VERB):
    """
    Module name may be specified, otherwhise we stack jump and use the
    one where this function is called.
    
    If which_r is set to 'wz', wee will use the werkzeug request and
    response objects
    """
    if module is None:
        module = sys._getframe(1).f_globals['__name__']
    scan_module(module, registry)
    return functools.partial(handle_request, module=module, request_class=Request, response_class=Response, dispatch=registry)


def scan_module(module_name, registry=None):
    mods = module_name.split('.')
    name = []
    if len(mods) > 1:
        name = mods[:-1]
    module_obj = __import__(module_name, globals(), locals(), name, -1)
    scan = venusian.Scanner(registry=registry).scan
    scan(module_obj)
