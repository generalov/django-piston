#!/usr/bin/env python
import unittest

from piston.mimer import Mimer, MimerLoaderRegistry


class MimerLoaderRegistryTestCase(unittest.TestCase):

    def setUp(self):
        self.registry = MimerLoaderRegistry()
        self.loadee = lambda data: "i got %s" % data

    def test_should_return_none_for_unknown_media_type(self):
        loadee = self.registry.get_loader_for_type("unknown/x-test")
        self.assertEquals(loadee, None)

    def test_should_register_loader_and_return_it_for_given_media_type(self):
        self.registry.register(self.loadee, ("text/x-test",))
        loadee = self.registry.get_loader_for_type("text/x-test")
        self.failUnlessEqual(loadee("hello"), "i got hello")

    def test_should_ignore_media_type_params(self):
        self.registry.register(self.loadee, ("text/x-test; charset=utf-8",))
        loadee = self.registry.get_loader_for_type("text/x-test; charset=latin-1")
        self.failUnlessEqual(loadee("hello"), "i got hello")

    def test_should_unregister_loader(self):
        self.registry.register(self.loadee, ("text/x-test",))
        loadee = self.registry.get_loader_for_type("text/x-test")

        # when unregister loadee
        self.registry.unregister(self.loadee)

        # then it did this for the last time...
        loadee = self.registry.get_loader_for_type("text/x-test")
        self.assertEquals(loadee, None)


class MimerUsingDefaultRegistryTestCase(unittest.TestCase):

    def setUp(self):
        self.loadee = lambda data: "i got %s" % data
        Mimer.register(self.loadee, ("text/x-test",))

    def tearDown(self):
        Mimer.unregister(self.loadee)

    def test_should_use_default_registry(self):
        mimer = Mimer("text/x-test; charset=latin-1")
        self.assertEquals("i got hello", mimer.translate("hello"))


class LoadeeTestCase(unittest.TestCase):

    def setUp(self):
        self.registry = MimerLoaderRegistry()

    def test_should_be_simple_callable(self):
        """Loadee should be simple function or callable."""
        self.registry.register(lambda raw_data: "x-test", ("text/x-test",))

        mimer = Mimer("text/x-test; charset=latin-1", registry=self.registry)
        data = mimer.translate("Hello, Piston!")
        self.assertEquals("x-test", data)

    def test_should_accept_optional_content_type_params(self):
        """Loadee should accept optional content type params."""
        def x_test_loadee(raw_data, **ctype_params):
            self.assertEquals(ctype_params["charset"], "latin-1")
            return "x-test"
        x_test_loadee.accepts_content_type_params = True
        self.registry.register(x_test_loadee, ("text/x-test",))

        mimer = Mimer("text/x-test; charset=latin-1", registry=self.registry)
        data = mimer.translate("Hello, Piston!")
        self.assertEquals("x-test", data)


if __name__ == "__main__":
    unittest.main()
