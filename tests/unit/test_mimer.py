#!/usr/bin/env python
import unittest

if __name__ == '__main__':
    import os, sys
    sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', '..'))

from piston.mimer import Mimer


class LoadeeTestCase(unittest.TestCase):

    def test_should_be_simple_callable(self):
        """Loadee should be simple function or callable."""
        def x_test_loadee(raw_data):
            return 'x-test'
        Mimer.register(x_test_loadee, ('text/x-test',))

        mimer = Mimer('text/x-test; charset=latin-1')
        data = mimer.translate("Hello, Piston!")
        self.assertEquals("x-test", data)

        Mimer.unregister(x_test_loadee)

    def test_should_accept_optional_content_type_params(self):
        """Loadee should accept optional content type params."""
        def x_test_loadee(raw_data, **ctype_params):
            self.assertEquals(ctype_params['charset'], 'latin-1')
            return 'x-test'
        x_test_loadee.accepts_content_type_params = True
        Mimer.register(x_test_loadee, ('text/x-test',))

        mimer = Mimer('text/x-test; charset=latin-1')
        data = mimer.translate("Hello, Piston!")
        self.assertEquals("x-test", data)

        Mimer.unregister(x_test_loadee)


if __name__ == '__main__':
    unittest.main()
