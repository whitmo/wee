import wee

@wee.get(r'^/other$')
def other(request):
    return 'other'
