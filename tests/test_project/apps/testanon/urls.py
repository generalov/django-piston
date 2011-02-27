from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication, HttpBasicSimple
from handlers import BlogpostHandler

auth = HttpBasicAuthentication(realm='TestApplication')

blogpost = Resource(handler=BlogpostHandler, authentication=auth)

urlpatterns = patterns('',
    url(r'^testanon/$', blogpost),

    # oauth entrypoints
    url(r'^oauth/request_token$', 'piston.authentication.oauth_request_token'),
    url(r'^oauth/authorize$', 'piston.authentication.oauth_user_auth'),
    url(r'^oauth/access_token$', 'piston.authentication.oauth_access_token'),
)

