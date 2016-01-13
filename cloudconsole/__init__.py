#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

import config
from cloudconsole.helpers import jinja_uptime_filter

app = Flask(__name__)

# configure logging
app.logger.addHandler(config.log_file_handler)

# register custom jinja2 filters
app.jinja_env.filters['uptime'] = jinja_uptime_filter

# Enable/Disable debug mode
app.debug = True if config.LOG_LEVEL.upper() == 'DEBUG' else False

# enable flask debugger
app.config['SECRET_KEY'] = 'F1a5KD3bu93r'
toolbar = DebugToolbarExtension(app)

import cloudconsole.views
