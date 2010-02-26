=====
 wee
=====

You could call it Webob augmented `itty
<http://github.com/toastdriven/itty/>`_ .  It borrows it's form but
allow for the use of a passed in Request or Response object. By
default, it uses the Request and Response from WebOb, as well as WebOb's.


Why?
====

We were working with `itty` and hit our head a few times.  We really
liked the way it worked though and thought we might fit it with our
favorite request and response objects.  106 lines later, wee was born
as the dispatcher for a wsgi app.


Basic Usage
===========

Here is a super simple pony app to show the basics of wee.  Pretty
much the same as itty except we use full regex strings::

     import wee
     from wsgiref.simple_server import make_server

     @wee.get(r'^/$')
     def ponytime(request):
         return "It's Pony time!"


     @wee.post(r'^/$'):
     def make_pony(request):
         ... make a pony ...


     @wee.put('^/(?P<pony_name>\w+)$'):
     def add_unicorn_horn(request, pony_name=None):
         ... change a pony ...


     @wee.delete('^/(?P<pony_name>\w+)$'):
     def kill_a_pony(request, pony_name):
         ... delete a pony ...

     srv = make_server(host, port, wee.make_app())
     srv.serve_forever()


Using a prefix
==============

Sometimes you want to hang a wee app on an existing app tree::

    import wee

    @wee.get('^/$')
    def logical_root(request):
        return "I'm an index"

    registry = wee.PrefixRegistry(prefix='/my/crazy/existing/dispatch/tree')

    wee.make_app(registry=prefix)


Experimental REST Container support
===================================

There is some rough support for creating simple CRUD containers like
so::

     import wee
     
     @wee.rest("^/candymountain")
     class UnicornStable(wee.Resource):
         subtype = 'unicorn_id'
         def get(self):
             ... your list of unicorns ...

         def post(self):
             name = self.request.POST['unicorn-name']
             ... make a unicorn ...
    
         def getitem(self, unicorn_id):
             ... serve a unicorn ...

         def put(self, unicorn_id):
             ... change a unicorn ...

         def delete(self, unicorn_id):
             ... kill a unicorn ...


The rest verb generates a series of regexes to dispatch upon for the
appropriate verbs with a special care to separate 'get' (/) and
'getitem' (/some_id).


Other Differences from itty
===========================

The only other main difference is that dispatch is scoped by the
module that defines the handler.  This means multiple wee apps can run
in the same process without clobbering each other.  

We don't give you are run command either, nor any adapters for popular
frameworks. Maybe later.

Coverage
========

coverage.py says 100% currently, but we could have more unittests
vs. stack tests.


Wait I'm Confused ...
=====================

"When do I use itty and when do I use wee?"

You probably shouldn't use either.  This is an experiment, so seems to
be itty.

If you are brave though, use `wee` when you want to do some itty or
sinatra like, but are using Webob. Use `itty` when you want some
totally contained in itself w/ no dependencies that requires little
configuration that you want to run as quickly as possible.


Credits
=======

`Daniel Lindsley <http://www.toastdriven.com/fresh/>`_ -- Author of `itty
<http://github.com/toastdriven/itty/>`_

Matt George and Whit Morriss --  Ax work on Wee
