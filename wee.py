from webob import Request, Response
from webob import exc
import functools
import inspect
import re
import sys
import venusian


class Verb(object):

    def __init__(self, url):
        self.url = url
        
    def __call__(self, func):
        func._wee_verb = self
        venusian.attach(func, self.add_handler)
        return func

    def add_handler(self, scanner, name, func):
        if scanner.registry is None:
            raise ValueError("No Scanner")
        handlers = scanner.registry[self.__class__.__name__.upper()]
        key = func.__module__, re.compile(func._wee_verb.url),
        if handlers.has_key(key):
            raise ValueError("Whoah there! You can't have the same regex for more than one "\
                             "function in a single module.")
        handlers[key]=func


class rest(Verb):
    """
    A special verb that takes a class factory rather than a function
    """
    _get_items = set(('put', 'getitem', 'delete'))
    verbs = ('put', 'post', 'get', 'delete', 'getitem')

    def make_exp(self, name, class_):
        exp = self.url
        if self.url.endswith('$'):
            return exp
        
        if name not in self._get_items:
            if not self.url.endswith('/'):
                exp = r'%s/?$' %self.url
            if not exp.endswith('$'):
                exp = r'%s$' %exp
            return exp

        if not self.url.endswith('/'):
            exp = "%s/" %self.url
        exp = r'%s(?P<%s>[^/]+)/?$' %(exp, class_.subtype)
        #print exp
        return exp

    def __call__(self, class_):
        venusian.attach(class_, self.add_handler)
        return class_
    
    def add_handler(self, scanner, name, class_):
        for method in self.verbs:
            for superclass in class_.mro():
                call = getattr(superclass, method, None)
                if not call or call.__module__ == 'wee':
                    continue
                handlers = scanner.registry.get(call.__name__.upper())
                if call.__name__ is 'getitem':
                    handlers = scanner.registry.get('GET')
                exp = self.make_exp(call.__name__, class_)
                key = class_, re.compile(exp),
                handlers[key] = call
                break


class Resource(object):
    """
    Base class for rest handling
    """
    
    subtype = "item_id"

    def __init__(self, request, **group):
        for key, val in group.items():
            setattr(self, key, val)
    
    def get(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def put(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class get(Verb):
    """ the get """


class post(Verb):
    """ the post """


class delete(Verb):
    """ the delete """


class put(Verb):
    """ the put """


class DispatchRegistry(dict):

    verb = dict(POST=post,
                GET=get,
                PUT=put,
                DELETE=delete)

    def __init__(self):
        for verb in self.verb:
            self[verb]=dict()

    def search(self, regex, request):
        """
        Template method
        """
        return regex.search(request.environ['PATH_INFO'])

    def dispatch(self, request):
        verb = self.get(request.method)
        for key in verb:
            source, regex, = key
            match = self.search(regex, request)
            handler = verb[key]
            if match is not None:
                group = match.groupdict()
                if callable(source):
                    instance = source(request)
                    args = inspect.getargspec(handler).args
                    new_args = [group.get(arg) for arg in args if group.get(arg)]
                    return handler(instance, *new_args)
                return handler(request, **group)

    def __call__(self, request):
        return self.dispatch(request)


class PrefixRegistry(DispatchRegistry):

    def __init__(self, prefix, strict=True):
        super(PrefixRegistry, self).__init__()
        self.prefix = prefix
        self.strict = strict
        if isinstance(prefix, basestring):
            self.prefix = [x for x in prefix.split('/') if x]

    def search(self, regex, request):
        pi = request.environ['PATH_INFO']
        if not pi.startswith('/'):
            pi = '/' + pi
        return regex.search(pi)

    def __call__(self, request):
        for element in self.prefix:
            path_sub = request.path_info_pop()
            if self.strict is True and path_sub != element:
                raise ValueError("path element: %s does not match prefix element: %s"\
                                 %(path_sub, element))
        return self.dispatch(request)


def handle_request(environ, start_response, dispatch=None, module=None, 
                   request_class=Request, response_class=Response):
    """
    The main handler. Dispatches to the user's code.
    """
    request = request_class(environ)
    try:
        response = dispatch(request)
        if response is None:
            raise exc.HTTPNotFound()
    except exc.WSGIHTTPException, e:
        return e(environ, start_response)
    except Exception, e:
        #return exc.HTTPServerError('Server Error')
        raise
    
    if isinstance(response, basestring):
        response = response_class(response)
    
    return response(environ, start_response)


def make_app(module=None, registry=None, walk=False):
    """
    Module name may be specified, otherwhise we stack jump and use the
    one where this function is called.
    
    If which_r is set to 'wz', wee will use the werkzeug request and
    response objects
    """
    if module is None:
        module = sys._getframe(1).f_globals['__name__']
    registry = scan_module(module, registry, walk=walk)
    return functools.partial(handle_request, module=module, request_class=Request, response_class=Response, dispatch=registry)


def scan_module(module_name, registry=None, walk=False):
    name = []
    if registry is None:
        registry = DispatchRegistry()

    module_obj = module_name
    if not inspect.ismodule(module_name):
        mods = module_name.split('.')
        if len(mods) > 1:
            name = mods[:-1]        
        module_obj = __import__(module_name, globals(), locals(), name, -1)
    scan = WeeScanner(registry=registry, walk=walk).scan
    scan(module_obj)
    return registry


class WeeScanner(venusian.Scanner):

    def invoke(self, name, ob):
        callbacks = getattr(ob, venusian.ATTACH_ATTR, None)
        if callbacks is not None:
            for callback in callbacks:
                callback(self, name, ob)
        
    def scan(self, package):
        """ Scan a Python package and any of its subpackages.  All
        top-level objects will be considered; those marked with
        venusian callback attributes will be processed.

        The ``package`` argument should be a reference to a Python
        package or module object.
        """
        for name, ob in inspect.getmembers(package):
            self.invoke(name, ob)

        if hasattr(package, '__path__') and getattr(self, 'walk', True) is True: # package, not module
            results = venusian.walk_packages(package.__path__, package.__name__+'.')
            for importer, modname, ispkg in results:
                __import__(modname)
                module = sys.modules[modname]
                for name, ob in inspect.getmembers(module, None):
                    self.invoke(name, ob)
    
