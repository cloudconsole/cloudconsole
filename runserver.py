#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from cloudconsole import app

DEBUG = False
if config.LOG_LEVEL.upper() == 'DEBUG':
    DEBUG = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=DEBUG)
