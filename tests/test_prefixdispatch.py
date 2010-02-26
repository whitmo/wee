import wee
import tests
from webtest import TestApp


@wee.get(r'^/$')
def index(request):
    return "the root"


@wee.get(r'^/pickles$')
def pickle(request):
    return "the pickles"


application = wee.make_app(registry=wee.PrefixRegistry('jar-of'))

class TestPrefixDispatch(tests.BaseCase):
    app = TestApp(application)

    def test_basic_dispatch(self):
        res = self.app.get('/jar-of')
        self.cmp(res.body, "the root")

        res = self.app.get('/jar-of/pickles')
        self.cmp(res.body, "the pickles")
