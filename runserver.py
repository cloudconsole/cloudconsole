#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from cloudconsole import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.port)
