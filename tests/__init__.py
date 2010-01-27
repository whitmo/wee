from webtest import TestApp
import functools
import unittest
import webob
import wee 


@wee.get(r"^/$")
def get_string(request):
    return  "I'm a string"


@wee.get(r"^/response$")
def get_response(request):
    return webob.Response("I'm a response")


@wee.post(r"^/$")
def postme(request):
    return "I'm a post"


class BaseCase(unittest.TestCase):
    def cmp(self, have, want):
        assert have == want, "\n%s != \n%s" %(have, want) 

application = functools.partial(wee.handle_request, module='tests')

class TestWee(BaseCase):
    app = TestApp(application)

    def test_get(self):
        res = self.app.get("/")
        self.cmp(res.status, '200 OK')
        self.cmp(res.body, "I'm a string") 
        
        res = self.app.get("/response")
        self.cmp(res.status, '200 OK')
        self.cmp(res.body, "I'm a response") 

    def test_post(self):
        res = self.app.post("/")
        self.cmp(res.status, '200 OK')
        self.cmp(res.body, "I'm a post") 


class TestSimpleAppFactory(BaseCase):

    def test_self_scoping(self):
        app = TestApp(wee.make_app())
        self.cmp(app.get("/").status, "200 OK")

            
