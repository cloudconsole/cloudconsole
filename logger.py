#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import config

log = logging.getLogger(__name__)
log.setLevel(logging.getLevelName(config.log_level.upper()))

if config.log_level.upper() == 'DEBUG':
    formatter = logging.Formatter('%(asctime)s '
                                  '%(levelname)s '
                                  '%(filename)s '
                                  '%(funcName)s '
                                  '%(lineno)d '
                                  '%(name)s '
                                  '%(thread)d '
                                  '%(threadName)s '
                                  '%(message)s ')
else:
    formatter = logging.Formatter('%(asctime)s '
                                  '%(levelname)s '
                                  '%(name)s '
                                  '%(message)s')

# create file handler which logs even debug messages
log_file_handler = logging.FileHandler(config.log_file)
log_file_handler.setFormatter(formatter)

log.addHandler(log_file_handler)
