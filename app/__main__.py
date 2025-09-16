from aiohttp import web

from . import app_factory
from . import misc

root_app = app_factory(misc.app)

web.run_app(root_app, host='localhost', port=8080)
