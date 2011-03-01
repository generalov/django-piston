#!/usr/bin/env python
import unittest


from django.conf import settings
settings.configured or settings.configure(DEBUG=True)


from requestfactory import RequestFactory
from piston.handler import BaseHandler
from piston.resource import Resource

from piston.utils import translate_request_data


class ApplicationXWwwFormUrlencodedTestCase(unittest.TestCase):

    def setUp(self):
        self.requestfactory = RequestFactory()
        self.content_type = "application/x-www-form-urlencoded"

    def test_data_should_be_empty_for_GET_requests(self):
        """Data should be empty for GET requests."""
        from django.http import QueryDict
        request = self.requestfactory.get('/?Hello=Piston')
        translate_request_data(request)
        self.assertEquals({}, request.data)

    def test_should_convert_form_POST_to_data(self):
        """Should translate form POST message body."""
        from django.http import QueryDict
        request = self.requestfactory.post('/', 'Hello=Piston',
                content_type=self.content_type)
        translate_request_data(request)
        self.assertTrue(isinstance(request.data, QueryDict))
        self.assertEquals([("Hello", "Piston")], request.data.items())

    def test_should_convert_form_PUT_to_data(self):
        """Should translate form PUT message body."""
        from django.http import QueryDict
        request = self.requestfactory.put('/', 'Hello=Piston',
                content_type=self.content_type)
        translate_request_data(request)
        self.assertEquals({}, request.POST)
        self.assertTrue(isinstance(request.data, QueryDict))
        self.assertEquals([("Hello", "Piston")], request.data.items())

    def test_should_convert_form_DELETE_to_data(self):
        """Should translate form DELETE message body."""
        # I'm sorry. The django test client has very strange DELETE method:
        # it converts data to a query and always sends request with empty body.
        request = self.requestfactory.delete('/', {'Hello':'Piston'},
                content_type=self.content_type)
        translate_request_data(request)
        self.assertEquals({}, request.POST)
        self.assertTrue(isinstance(request.data, dict))
        self.assertEquals(dict(), request.data)


class ApplicationJSONTestCase(unittest.TestCase):

    def setUp(self):
        self.requestfactory = RequestFactory()
        self.content_type = "application/json"

    def test_should_convert_form_PUT_to_data(self):
        """Should translate a JSON in a body of a PUT request."""
        request = self.requestfactory.put('/', '{"Hello":"Piston"}',
                content_type=self.content_type)
        translate_request_data(request)
        self.assertEquals({}, request.POST)
        self.assertEquals({"Hello": "Piston"}, request.data)


if __name__ == '__main__':
    unittest.main()
