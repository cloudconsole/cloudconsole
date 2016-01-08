#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from datastore import es


def put(docs, doc_type):
    if config.DATA_STORE == 'es':
        conn = es.ES(doc_type=doc_type)

    return conn.put_docs(docs=docs)


def init_datastore():
    if config.DATA_STORE == 'es':
        conn = es.ES()
        conn.init_datastore()

