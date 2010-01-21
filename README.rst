=====
 wee
=====

You could call it Webob augmented `itty
<http://github.com/toastdriven/itty/>`_ .  It borrows heavily from
itty but allow for the use of a passed in Request or Response object


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


srv = make_server(host, port, wee.make_simple_application())
srv.serve_forever()



Other Differences from itty
===========================

The only other main difference is that dispatch is scoped by the
module that defines the handler.  This means multiple wee apps can run
in the same process without clobbering each other.  

We still cannot define multiple apps in the same module, but hey, this
isn't suppose to be fancy, it's `wee`.

We don't give you are run command either, nor any adapters for popular
frameworks. Maybe later.



Wait I'm Confused ...
=====================

"When do I use itty and when do I use wee?"

You probably shouldn't use either.  This is an experiment, so seems to
be itty.

If you are brave though, use wee when you want to do some itty like,
but are using Webob. Use itty when you want some totally contained in itself w/ no
dependencies that requires little configuration that you want to run
as quickly as possible.


Werkzeug Support
================

`wee.make_simple_application` has a werkzeug flag that creates an
application that uses the Werkzeug Request and Response rather than
the default Webob one.  This is more experiment than the very
experimental experiment that wee is.

