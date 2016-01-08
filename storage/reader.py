#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from datastore import es


def get_doc(doc_id, doc_type=None):
    if config.DATA_STORE == 'es':
        conn = es.ES(doc_type=doc_type)

    results = conn.get_doc(doc_id=doc_id)
    if results:
        return results
    else:
        return None


def get_all_match(query_str, doc_type=None):
    if config.DATA_STORE == 'es':
        conn = es.ES(doc_type=doc_type)

        return conn.get_all_match(query_str=query_str)


def get_elbs_by_instance(instance_id):
    if config.DATA_STORE == 'es':
        conn = es.ES()

        return conn.get_elbs_by_instance(instance_id=instance_id)
