import os
import logging
import signal

from tornado import ioloop
from tornado import httpserver
from tornado import web

from easy2use.globals import log


LOG = logging.getLogger('tornado.application')


def stop_ioloop(signum, frame):
    LOG.info('catch signal %s, stop ioloop', signum)

    ioloop.IOLoop.instance().add_callback_from_signal(
        lambda: ioloop.IOLoop.instance().stop())



class Index(web.RequestHandler):

    def get(self):
        self.set_status(200)
        self.finish('<h1> hello, world </h1>')


class TornadoApp(object):
    def __init__(self, routes, template_path='templates', static_path='static',
                 develop=False) -> None:
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

        ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    log.basic_config(logging.DEBUG)
    app = TornadoApp([('/', Index)])
    app.start()
