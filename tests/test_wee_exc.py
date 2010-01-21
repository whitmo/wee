from tests import BaseCase
from webob import exc
from webtest import TestApp, AppError
import functools
import wee 


@wee.get(r"^/pony$")
def throw_error(request):
    raise exc.HTTPNotFound("404")


@wee.get(r'^/over-there$')
def redirect(request):
    raise exc.HTTPFound(location="http://over-here")


application = functools.partial(wee.handle_request, module=__name__)


class TestExceptions(BaseCase):
    app = TestApp(application)
    
    def test_error(self):
        try:
            res = self.app.get("/pony")
        except AppError, e:
            assert e.args[0].startswith("Bad response: 404 Not Found")

    def test_redirect(self):
        res = self.app.get("/over-there")
        assert res.status == '302 Found'
        assert res.location == 'http://over-here'
        

