import wee
import tests
from webtest import TestApp


@wee.rest(r"^/empty")
class EmptyResource(wee.Resource):
    """
    Empty to check raises
    """
    
@wee.rest(r"^/")
class Resource(wee.Resource):
    def getitem(self, item_id):
        return "you got subserved: %s" %(item_id)
    
    def get(self):
        return "You got served"

    def post(self):
        return "posted"

    def put(self, item_id):
        return "put: %s" %(item_id)

    def delete(self, item_id):
        return "delete %s" %item_id


@wee.rest(r"^/wholepath/$")
class ResourceMoney(Resource):
    pass


@wee.rest(r"^/addslash")
class ResourceAddSlash(Resource):
    pass


application = wee.make_app()


class TestREST(tests.BaseCase):
    app = TestApp(application)

    def test_empty(self):
        res = self.app.get("/empty")
        
    def test_get(self):
        res = self.app.get("/")
        self.cmp(res.status, '200 OK')
        self.cmp(res.body, "You got served") 

    def test_getitem(self):
        res = self.app.get("/some_id")
        self.cmp(res.status, '200 OK')
        self.cmp(res.body, "you got subserved: some_id") 

    def test_addslash(self):
        res = self.app.get("/addslash/some_id")
        self.cmp(res.status, '200 OK')
        self.cmp(res.body, "you got subserved: some_id")
        
    def test_delete(self):
        res = self.app.delete("/some_id")
        self.cmp(res.status, '200 OK') # maybe should be something else
        self.cmp(res.body, 'delete some_id')

    def test_delete_empty(self):
        # not sure if this is right... expected a 500 for the
        # notimplemented
        res = self.app.delete("/empty/some_id", status=404)


def test_verb_expression_gen():
    verb = wee.rest("^/")
    assert verb.make_exp("get", wee.Resource) == r'^/$'
    assert verb.make_exp("getitem", wee.Resource) == r'^/(?P<item_id>[^/]+)/?$'
    assert verb.make_exp("put", wee.Resource) \
           == verb.make_exp("getitem", wee.Resource) \
           == verb.make_exp("delete", wee.Resource) \


def test_verb_expression_addslash():
    verb = wee.rest("^/slug")
    assert verb.make_exp("get", wee.Resource) == r'^/slug/?$'


def test_verb_expression_no_change():
    verb = wee.rest("^/slug/$")
    assert verb.make_exp("get", wee.Resource) == r'^/slug/$'
