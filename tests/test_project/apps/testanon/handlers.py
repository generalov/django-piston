from piston.handler import AnonymousBaseHandler, BaseHandler


class AnonymousBlogpostHandler(AnonymousBaseHandler):
    allowed_methods = ('GET', )

    def read(self, request):
        return 'Ok'

class BlogpostHandler(BaseHandler):
    anonymous = AnonymousBlogpostHandler

    allowed_methods = ('GET', 'POST', )
