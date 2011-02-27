from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import simplejson
from django.utils.http import urlencode
from django.conf import settings

import base64

from handlers import AnonymousBaseHandler


class MainTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('admin', 'admin@world.com', 'admin')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.save()
        self.auth_string = 'Basic %s' % base64.encodestring('admin:admin').rstrip()

    def tearDown(self):
        self.user.delete()


class BasicAuthTest(MainTests):

    def test_should_accept_allowed_method(self):
        self.failUnless('GET' in AnonymousBaseHandler.allowed_methods)
        response = self.client.get('/api/testanon/')
        self.assertEquals(response.content, '"Ok"')
        self.assertEquals(response.status_code, 200)

    def test_should_deny_not_allowed_method(self):
        self.assertFalse('POST' in AnonymousBaseHandler.allowed_methods)
        response = self.client.post('/api/testanon/')
        self.assertEquals(response.status_code, 401)
