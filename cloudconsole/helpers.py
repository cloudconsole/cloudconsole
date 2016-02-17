#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from datetime import datetime
from datetime import timedelta

import humanize
from flask import render_template


def render_page(template, query=None, page_data=None, extra_vars=None):
    if page_data:
        return render_template(template,
                               s_query=query,
                               page_data=page_data,
                               extra_vars=extra_vars)
    else:
        return render_template('notfound.html', query=query)


def jinja_uptime_filter(date_time):
    # time_format = '%Y-%m-%dT%H:%M:%S+00:00'
    epoch_time = datetime(1970, 1, 1)
    epoch_cur_time = ((datetime.utcnow() - timedelta(minutes=10)) -
                      epoch_time).total_seconds()

    launch_time = date_time
    epoch_launch_time = (launch_time - epoch_time).total_seconds()
    epoch_uptime = epoch_cur_time - epoch_launch_time

    uptime = re.sub(r'\b ago', '', humanize.naturaltime(epoch_uptime))

    return uptime

