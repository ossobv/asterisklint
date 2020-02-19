import falcon  # >=2.0.0
from io import BufferedWriter, BytesIO
from os import path
from wsgiref.handlers import SimpleHandler
from wsgiref.simple_server import WSGIRequestHandler, make_server

from asterisklint import FileDialplanParser
from asterisklint.alintver import version_str
from asterisklint.defines import MessageDefManager


class HttpNotImplementedError(falcon.HTTPBadRequest):
    "Instead of NotImplementedError; for better feedback."
    def __init__(self, description):
        super().__init__('Feature Not Implemented', description)


class NamedBytesIO(BytesIO):
    def __init__(self, name, data):
        self.name = name
        super().__init__(data)


class UploadedFileOpener:
    def __init__(self, filename, filedata):
        self.name = filename
        assert isinstance(filedata, bytes)
        self.data = filedata

    def __call__(self, filename):
        if self.name != filename:
            raise HttpNotImplementedError(
                'Include files are not supported in the web interface.')

        return NamedBytesIO(self.name, self.data)


def collect_messages():
    ret = []
    for msgtype, msgs in MessageDefManager.raised.items():
        ret.extend(msgs)
    ret.sort(key=(lambda x: (
        x.where.filename, x.where.lineno, type(x).__name__)))
    MessageDefManager.reset()  # very thread-unsafe, this!
    return ret


def max_body(limit):
    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = (
                'The size of the request is too large. The body must not '
                'exceed {limit} bytes in length.'.format(limit=limit))
            raise falcon.HTTPPayloadTooLarge('Request body is too large', msg)
    return hook


class EnvironmentCheckMiddleware:
    def process_request(self, req, resp):
        if req.env['wsgi.multithread']:
            raise HttpNotImplementedError(
                'AsteriskLint is single-threaded; '
                'make sure your wsgi daemon is too.')


# class DebugLogMiddleware:
#     def process_response(self, req, resp, resource):
#         bytes_ = resp.body and len(resp.body) or 0
#         print(
#             '{ip} - - [{time}] "{method} {path} HTTP/x.x" '
#             '{code} {bytes}'.format(
#                 ip=req.env['REMOTE_ADDR'],
#                 time=datetime.utcnow().strftime('%d/%b/%Y:%H:%M:%S +0000'),
#                 method=req.method,
#                 path=req.path,
#                 code=resp.status.split(' ', 1)[0],
#                 bytes=bytes_))


class Index:
    index_html = open(
        path.join(path.dirname(__file__), 'index.html'), 'r').read()

    def on_get(self, req, resp):
        # print(req.env['REMOTE_ADDR'])
        resp.content_type = 'text/html; charset=utf-8'
        resp.body = self.index_html


class Healthz:
    """
    Readiness/liveness probes for Kubernetes.

    livenessProbe/readinessProbe:
      httpGet:
        path: /healthz
        port: 80
      initialDelaySeconds: 10
      timeoutSeconds: 5
    """
    def on_get(self, req, resp):
        resp.content_type = 'text/plain; charset=utf-8'
        resp.body = 'OK\nasterisklint = {}\n'.format(version_str)


class DialplanCheck:
    @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp):
        # Reading POSTed FILEs:
        #   https://falcon.readthedocs.io/en/stable/user/faq.html
        #     #how-can-i-access-posted-files
        # Reading JSON:
        #   https://falcon.readthedocs.io/en/stable/api/api.html
        #     #falcon.RequestOptions
        # > A dict-like object that allows you to configure the
        # > media-types that you would like to handle. By default, a
        # > handler is provided for the application/json media type.
        filename = 'extensions.conf'

        # {"files": {"FILENAME": "FILEDATA"}}
        filedata = req.media['files'][filename].encode('utf-8')
        opener = UploadedFileOpener(filename, filedata)

        parser = FileDialplanParser(opener=opener)
        parser.include(filename)
        dialplan = next(iter(parser))
        dialplan.walk_jump_destinations()
        del dialplan

        issues = {filename: []}
        msgs = collect_messages()
        for msg in msgs:
            formatted = msg.message.format(**msg.fmtkwargs)
            issues[msg.where.filename].append({
                'line': msg.where.lineno,
                'class': msg.__class__.__name__,
                'desc': formatted,
            })

        resp.media = {
            'results': issues,
            'asterisklint': {'version': version_str},
        }


MessageDefManager.muted = True  # no messages to stderr

middleware = [EnvironmentCheckMiddleware()]

application = falcon.API(middleware=middleware)
application.req_options.strip_url_path_trailing_slash = True  # allow /healthz/
application.add_route('/', Index())
application.add_route('/healthz', Healthz())
application.add_route('/dialplan-check', DialplanCheck())


if __name__ == '__main__':
    class MySimpleHandler(SimpleHandler):
        def close(self):
            try:
                # Add request logging.
                self.request_handler.log_request(
                    self.status.split(' ', 1)[0], self.bytes_sent)
            finally:
                super().close()

    class MyWSGIRequestHandler(WSGIRequestHandler):
        def handle(self):
            """
            Handle a single HTTP request. Shamelessly copied from Python
            3.5 wsgiref simple_server. Adjusted the SimpleHandler to set
            multithread=False.
            """
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return

            if not self.parse_request():  # an error code has been sent, exit
                return

            # Avoid passing the raw file object wfile, which can do partial
            # writes (Issue 24291)
            stdout = BufferedWriter(self.wfile)
            try:
                handler = MySimpleHandler(
                    self.rfile, stdout, self.get_stderr(), self.get_environ(),
                    multithread=False, multiprocess=False)
                handler.request_handler = self      # backpointer for logging
                handler.run(self.server.get_app())
            finally:
                stdout.detach()

    # Spawn server.
    httpd = make_server(
        '127.0.0.1', 8080, application, handler_class=MyWSGIRequestHandler)
    httpd.serve_forever()
