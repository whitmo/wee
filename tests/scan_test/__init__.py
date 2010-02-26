#
import wee

@wee.get(r'^/$')
def index(request):
    return 'index'
