from webtest import TestApp
import unittest
import webob
from pprint import pprint
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



reg = wee.DispatchRegistry()
application = wee.make_app(registry=reg, walk=False)

def test_reg_consitency():
    for module, patt in reg['GET'].keys():
        assert module == 'tests', "Scanning is walking more than just this module"


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


sandboxed = wee.make_app()


class TestSBWee(TestWee):
    app = TestApp(sandboxed)

    
class TestSimpleAppFactory(BaseCase):

    def test_self_scoping(self):
        app = TestApp(wee.make_app(registry=wee.DispatchRegistry()))
        self.cmp(app.get("/").status, "200 OK")






            
