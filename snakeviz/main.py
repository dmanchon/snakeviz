#!/usr/bin/env python

import os.path
from pstats import Stats

try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus

import aiohttp.web
import aiohttp_jinja2
import jinja2
from .stats import table_rows, json_stats
import cProfile, pstats, io
import os
import tempfile
from yarl import URL

pr = None
path = 'stats'

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'debug': True,
    'gzip': True
}


def viz_handler(request):
    pr.disable()
    try:
        if 'X-VirtualHost-Monster' in request.headers:
            base_url = request.headers['X-VirtualHost-Monster']
            if base_url[-1] == '/':
                base_url = base_url[:-1]
            p = str(URL(base_url).relative())
            prefix = p.split('/oauth/')[0]
            prefix = '' if prefix == '/' else prefix
            if prefix != '':
                path = prefix + '/' + path
        sio = io.StringIO()
        ps = pstats.Stats(pr, stream=sio)
        temp = tempfile.NamedTemporaryFile()
        ps.dump_stats(temp.name)
        s = Stats(temp.name)
        temp.close()
        context = {
            'table_rows': table_rows(s),
            'callees': json_stats(s), 
            'profile_name': temp.name, 
            'path': path
        }
        response = aiohttp_jinja2.render_template('viz.html', request, context)
    except:
        raise RuntimeError('Could not read %s.' % profile_name)
    finally:
        pr.enable()
    
    return response

def get_app(profile, app_path):
    global pr, path
    pr = profile
    path = app_path
    app = aiohttp.web.Application()
    app.router.add_static('/static', settings['static_path'])
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader(settings['template_path']))
    app.router.add_get('/', viz_handler)
    return app