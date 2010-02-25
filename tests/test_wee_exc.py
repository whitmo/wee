from tests import BaseCase
from webob import exc
from webtest import TestApp
import wee 


@wee.get(r"^/pony$")
def throw_error(request):
    raise exc.HTTPNotFound("404")


@wee.get(r'^/over-there$')
def redirect(request):
    raise exc.HTTPFound(location="http://over-here")


application = wee.make_app()


class TestExceptions(BaseCase):
    app = TestApp(application)
    
    def test_error(self):
        res = self.app.get("/pony", status=404)
        assert res.status_int == 404
    
    def test_redirect(self):
        res = self.app.get("/over-there")
        assert res.status == '302 Found'
        assert res.location == 'http://over-here'
        

