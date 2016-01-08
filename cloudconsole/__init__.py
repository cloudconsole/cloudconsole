#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

import config
from cloudconsole.helpers import jinja_uptime_filter

app = Flask(__name__)
app.logger.addHandler(config.log_file_handler)
app.jinja_env.filters['uptime'] = jinja_uptime_filter

import cloudconsole.views
