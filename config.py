#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import abspath, dirname


app_dir = dirname(abspath(__file__))

port = 5000

regions = ['us-east-1', 'us-west-1', 'us-west-2', 'eu-west-1']

# Database configuration
mongodb_uri = 'mongodb://localhost:27017/'
db_name = 'cloudconsole'  # Database name

enabled_services = {'aws': True,
                    'ultradns': True,
                    'dnsmadeeasy': False}

# log config
log_file = '/tmp/cloudconsole.log'
log_level = 'DEBUG'
