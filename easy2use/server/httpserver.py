import logging
import os

import flask
from flask import views
from gevent import pywsgi

from easy2use import net

LOG = logging.getLogger(__name__)
ROUTE = os.path.dirname(os.path.abspath(__file__))

INDEX_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>FLuent HTTP Server</title>
    </head>
    <body>
        <h3>Fluent HTTP Server</h3>
        <p>Please set your rules</p>
    </body>
</html>
"""


class IndexView(views.MethodView):

    def get(self):
        return INDEX_HTML


class WsgiServer:
    RULES = [(r'/', IndexView.as_view('index')), ]

    def __init__(self, name, host=None, port=80, template_folder=None,
                 static_folder=None, converters_ext=None, secret_key=None):
        self.host = host or net.get_internal_ip()
        self.port = port
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.app = flask.Flask(name,
                               template_folder=self.template_folder,
                               static_folder=self.static_folder)
        if secret_key:
            self.app.config['SECRET_KEY'] = secret_key
        if converters_ext:
            for ext_name, cls in converters_ext:
                self.app.url_map.converters[ext_name] = cls

        self._register_rules()

        self.app.jinja_env.variable_start_string = '[['
        self.app.jinja_env.variable_end_string = ']]'
        self.app.config['SERVER_NAME'] = '{}:{}'.format(self.host, self.port)

        self.app.before_request(self.before_request)
        self.server = None

    def before_request(self):
        """Do someting here before reqeust"""
        return

    def _register_rules(self):
        LOG.debug('register rules')
        for url, view_func in self.RULES:
            self.app.add_url_rule(url, view_func=view_func)

    def start(self, develoment=False, use_reloader=False):
        LOG.info('strarting server: http://%s:%s', self.host, self.port)
        if develoment:
            self.app.run(host=self.host, port=self.port, debug=True,
                         use_reloader=use_reloader)
        else:
            self.server = pywsgi.WSGIServer((self.host, self.port), self.app)
            self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.stop()
