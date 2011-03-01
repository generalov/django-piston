import os
import fnmatch
import unittest


def discover(start_dir, pattern="test*.py", top_level_dir=None):
    lsdir = []
    cwd = os.getcwd()
    os.chdir(top_level_dir or start_dir or '.')

    for root, dirs, files in os.walk('.'):
        for dname in dirs:
            if os.path.exists(os.path.join(dname, '__init__.py')):
                lsdir.append(os.path.join(root, dname))
        for fname in files:
            if fnmatch.fnmatch(fname, pattern):
                lsdir.append(os.path.join(root, fname))
    modules = [os.path.splitext(path)[0].lstrip('.').lstrip(os.sep).\
                replace(os.path.sep, '.') for path in lsdir]

    testSuite = unittest.TestSuite()
    for name in modules:
        try:
            mod = __import__(name, globals(), locals(), ['suite'])
            suitefn = getattr(mod, 'suite')
            testSuite.addTest(suitefn())
        except (ImportError, AttributeError):
            # else, just load all the test cases from the module.
            testSuite.addTest(unittest.defaultTestLoader.loadTestsFromName(name))

    os.chdir(cwd)

    return testSuite

def suite():
    return discover(os.path.dirname(__file__))


if __name__ == '__main__':
    from django.conf import settings
    settings.configured or settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                    'SUPPORTS_TRANSACTIONS': True,
                },
            }
    )

    unittest.TextTestRunner().run(suite())
