#!/usr/bin/env python
import unittest


class ParseContentTypeHeaderTestCase(unittest.TestCase):

    def setUp(self):
        from piston.mimer import parse_content_type_header
        self.parse_content_type_header = parse_content_type_header

    def test_should_parse_header_with_content_type_only(self):
        """Should parse header with content type only."""
        header = 'text/html'
        ctype, options = self.parse_content_type_header(header)
        self.assertEquals(ctype, 'text/html')
        self.assertEquals(options, {})

    def test_should_parse_header_with_charset(self):
        """Should parse header with charset."""
        header = 'text/html; charset=utf-8'
        ctype, options = self.parse_content_type_header(header)
        self.assertEquals(ctype, 'text/html')
        self.assertEquals(options, {'charset': 'utf-8'})


if __name__ == '__main__':
    import os, sys
    sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', '..'))
    unittest.main()
