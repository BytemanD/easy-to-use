import argparse
import functools
import json
import logging
import pathlib
import signal

from tornado import ioloop
from tornado import httpserver
from tornado import web

from easy2use.globals import log

LOG = logging.getLogger('tornado.application')

INDEX = 'index.html'


def stop_ioloop(signum, frame):
    LOG.info('catch signal %s, stop ioloop', signum)

    ioloop.IOLoop.instance().add_callback_from_signal(
        lambda: ioloop.IOLoop.instance().stop())


def with_response(return_code=200):

    def _response(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                resp = func(self, *args, **kwargs)
            except Exception as e:
                LOG.exception(e)
                resp = 500, f'Internal Server error: {str(e)}'
            if isinstance(resp, tuple):
                status, body = resp
            else:
                status = return_code
                body = resp
            self.set_status(status)
            self.finish(body)

        return wrapper

    return _response


class BaseReqHandler(web.RequestHandler):
    ENABLE_CROSS_DOMAIN = False

    def set_default_headers(self):
        super().set_default_headers()
        if self.ENABLE_CROSS_DOMAIN:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Headers', '*')
            self.set_header('Access-Control-Allow-Max-Age', 1000)
            self.set_header('Access-Control-Allow-Methods',
                            'GET, POST, PUT, DELETE, PATCH, OPTIONS')

    def return_resp(self, status, data):
        self.set_status(status)
        self.finish(data)

    def _get_body(self):
        return json.loads(self.request.body)

    @with_response(return_code=204)
    def options(self, *args, **kwargs):
        LOG.debug('options request')


class Index(web.RequestHandler):

    def get(self):
        self.redirect(INDEX)


class HtmlHandler(BaseReqHandler):

    def get(self):
        try:
            self.render(self.request.path[1:])
        except FileNotFoundError:
            self.set_status(404)
            self.finish({'error': f'{self.request.path[1:]} not found'})


class TornadoApp(object):

    def __init__(self, routes, template_path='templates', static_path='static',
                 develop=False):
        self.routes = routes
        self.template_path = template_path
        self.develop = develop
        self.static_path = static_path

    def start(self, port=80, address=None, num_processes=1,
              max_body_size=None):
        signal.signal(signal.SIGINT, stop_ioloop)
        signal.signal(signal.SIGTERM, stop_ioloop)

        app = web.Application(self.routes, debug=self.develop,
                              template_path=self.template_path,
                              static_path=self.static_path)

        if self.develop:
            LOG.warn('Starting sevice with develop mode')
            app.listen(port, address=address)
        else:
            server = httpserver.HTTPServer(app, max_body_size=max_body_size)
            server.bind(port)
            server.start(num_processes=num_processes)

        LOG.info('Staring server on port %s:%s ...', address, port)
        LOG.debug('template path: %s', self.template_path)
        LOG.debug('static path: %s', self.static_path)

        if not pathlib.Path(self.template_path).exists():
            LOG.warning('template path not exists.')
        if not pathlib.Path(self.static_path).exists():
            LOG.warning('static path not exists.')

        ioloop.IOLoop.instance().start()


def get_routes():
    return [
        (r'/', Index),
        (r'/.+\.html', HtmlHandler)
    ]


def init(enable_cross_domain=False, index_redirect=None):
    global INDEX

    if enable_cross_domain:
        BaseReqHandler.ENABLE_CROSS_DOMAIN = True
    if index_redirect:
        INDEX = index_redirect


def main():
    global INDEX

    parser = argparse.ArgumentParser()
    parser.add_argument('port', default=80, nargs='?',
                        help='Port, defaults to 80')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Use DEBUG level for log')
    parser.add_argument('-t', '--template', default='./template',
                        help='Template path, defaults to ./template')
    parser.add_argument('-s', '--static', default='./static',
                        help='Static path, defaults to ./static')
    parser.add_argument('-r', '--root-redirect', default=INDEX,
                        help=f'Root URL redirect to, defaults to {INDEX}')
    args = parser.parse_args()
    log.basic_config(args.debug and logging.DEBUG or logging.INFO)
    if INDEX != args.root_redirect:
        INDEX = args.root_redirect

    app = TornadoApp(get_routes(),
                     template_path=args.template,
                     static_path=args.static)
    app.start(port=args.port)


if __name__ == '__main__':
    main()
