"""
There are many beautiful libraries to deal with HTTP headers:

- `httpheader <http://deron.meranda.us/python/httpheader/httpheader.py>`
- `Werkzeug <https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/http.py>`
- `Paste <https://bitbucket.org/ianb/paste/src/tip/paste/httpheaders.py>`

If this __file__ will become to grow please consider to use one of whem. :-)
"""
__all__ = ['Mimer', 'MimerDataException', 'translate_request_data']


from email.message import Message


class MimerDataException(Exception):
    """
    Raised if the content_type and data don't match
    """
    pass


class Mimer(object):
    TYPES = dict()

    def __init__(self, media_type):
        self._media_type = media_type.strip()

    @classmethod
    def from_request(cls, request):
        """Create a `Mimer` from a django.http.HttpRequest."""
        media_type = request.META.get("CONTENT_TYPE", "")
        return cls(media_type)

    @property
    def media_type(self):
        """Return entry media type."""
        return self._media_type

    @property
    def content_type(self):
        """Return content type (media type without parameters).

        For example when media_type is "text/html; charset=ISO-8859-4" this
        returns "text/html"
        """
        media_type = self.media_type
        if ';' in media_type:
            content_type = media_type.split(';', 1)[0].strip()
        else:
            content_type = media_type
        return content_type

    @property
    def is_form_data(self):
        """Retrun True then a ``content_type`` is type of form data."""
        return self.content_type in (
                "application/x-www-form-urlencoded", 
                "multipart/form-data")

    @property
    def loadee(self):
        """Return a loader for our media type or None."""
        return Mimer.loader_for_type(self.media_type)

    def translate(self, raw_data):
        """
        Will try to deserialize the ``raw_data`` according to an our
        media_type. This will work for JSON, YAML, XML and Pickle.
        """
        try:
            return self.loadee(raw_data)
        except (TypeError, ValueError):
            # This also catches if loadee is None.
            raise MimerDataException

    # TODO: extract these classmethods to a MimerRegistry.

    @classmethod
    def loader_for_type(cls, media_type):
        """
        Gets a function ref to deserialize content
        for a certain mimetype.
        """
        loader = None
        content_type, params = parse_content_type_header(media_type)
        for loadee, mimes in Mimer.TYPES.iteritems():
            if content_type in mimes:
                if getattr(loadee, 'accepts_content_type_params', False):
                    loader = lambda data: loadee(data, **params)
                else:
                    loader = loadee
                break
        return loader

    @classmethod
    def register(cls, loadee, types):
        cls.TYPES[loadee] = types

    @classmethod
    def unregister(cls, loadee):
        return cls.TYPES.pop(loadee)


def translate_request_data(request):
    """Translate nested datastructs into `request.data`.
    
    And set `request.content_type` with content type for request data
    (excluding a ``Content-type`` parameters).
    """
    mimer = Mimer.from_request(request)
    request.content_type = mimer.content_type
    request.data = dict()
    if has_body(request):
        if not request.content_type:
            pass
        elif mimer.is_form_data:
            # Use Django to translate form data.
            django_coerse_to_post(request)
            request.data = request.POST
            # When the request contains a form data and a request.method is
            # a POST it is no bad to leave a request.POST as alias for
            # a request.data for compability with Django's world.
            if request.method != 'POST':
                request.POST = dict()
        else:
            request.data = mimer.translate(request.raw_post_data)
            # We override request.POST because of it contains
            # a QueryDict with garbage when data is not a form.
            request.POST = dict()

def has_body(request):
    """Determinate a presence of a message body in a ``request``."""
    # "The presence of a message-body in a request is signaled by the
    # inclusion of a Content-Length or Transfer-Encoding header field in
    # the request's message-headers."
    # See http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.3
    return 'CONTENT_LENGTH' in request.META or \
           'HTTP_TRANSFER_ENCODING' in request.META

def parse_content_type_header(header):
    """Parse a ``Content-Type`` like header into a tuple with the content type
    and the options.

    >>> parse_content_type_header('text/plain; charset=utf-8')
    ('text/plain, {'charset': 'utf-8'})

    :param header: the header to parse.
    :return: (str, options)
    """
    msg = Message()
    msg['Content-type'] = header
    ctype, params = msg.get_content_type(), dict(msg.get_params()[1:])
    return ctype, params

def django_coerse_to_post(request):
    """
    Django doesn't particularly understand REST. In case we send data over
    PUT, Django won't actually look at the data and load it. We need to twist
    its arm here.

    The try/except abominiation here is due to a bug in mod_python. This should
    fix it.
    """
    method = request.method
    if method == "POST":
        # Assume it's already coersed 
        return

    # Bug fix: if _load_post_and_files has already been called, for
    # example by middleware accessing request.POST, the below code to
    # pretend the request is a POST instead of a PUT will be too late
    # to make a difference. Also calling _load_post_and_files will result
    # in the following exception:
    #   AttributeError: You cannot set the upload handlers after the upload has been processed.
    # The fix is to check for the presence of the _post field which is set
    # the first time _load_post_and_files is called (both by wsgi.py and
    # modpython.py). If it's set, the request has to be 'reset' to redo
    # the query value parsing in POST mode.
    if hasattr(request, '_post'):
        del request._post
        del request._files

    try:
        request.method = "POST"
        request._load_post_and_files()
        request.method = method
    except AttributeError:
        request.META['REQUEST_METHOD'] = 'POST'
        request._load_post_and_files()
        request.META['REQUEST_METHOD'] = method

