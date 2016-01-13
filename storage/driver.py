#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from elasticsearch import Elasticsearch
from elasticsearch import exceptions
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q

import config
from config import log


class Writer(object):
    """Storage Reader Object"""

    def __init__(self, doc_type=None):
        super(Writer, self).__init__()
        self.db_name = config.DB_NAME
        self.doc_type = doc_type

        if self.doc_type == 'aws_ec2':
            self.id_identifier = 'InstanceId'
        elif self.doc_type == 'aws_elb':
            self.id_identifier = 'LoadBalancerName'
        else:
            self.id_identifier = None

        self.conn = Elasticsearch(config.ES_NODES)

    def init_datastore(self):
        schema_fd = open('%s/storage/schema/es.json' % config.APP_DIR)
        schema = json.load(schema_fd)

        resp = self.conn.indices.create(index=self.db_name,
                                        ignore=400,
                                        body=schema)

        if 'acknowledged' in resp:
            log.info("Index created successfully")
        else:
            log.debug("Index already exists")

    def put_docs(self, docs):
        for doc in docs:
            self.write(doc)

        success = True
        return success

    def write(self, doc):
        if self.id_identifier:
            self.conn.index(index=self.db_name,
                            doc_type=self.doc_type,
                            id=doc[self.id_identifier],
                            body=doc)
        else:
            self.conn.index(index=self.db_name,
                            doc_type=self.doc_type,
                            body=doc)

        success = True
        return success

    def update(self, doc):
        old_doc = self.get_doc(doc_id=doc[self.id_identifier])
        print(old_doc)
        print(doc)
        # status = self.conn.update(index=self.db_name,
        #                           doc_type=self.doc_type,
        #                           id=doc[self.id_identifier],
        #                           body=doc)

        return True

    def doc_exists(self, doc_id):
        pass


class Reader(object):
    """Storage Reader Object"""

    def __init__(self, doc_type=None):
        super(Reader, self).__init__()
        self.db_name = config.DB_NAME
        self.doc_type = doc_type

        if self.doc_type == 'aws_ec2':
            self.id_identifier = 'InstanceId'
        elif self.doc_type == 'aws_elb':
            self.id_identifier = 'LoadBalancerName'
        else:
            self.id_identifier = None

        self.conn = Elasticsearch(config.ES_NODES)

    def get_instance_by_id(self, doc_id):
        try:
            res = self.conn.get(index=self.db_name,
                                doc_type=self.doc_type,
                                id=doc_id)
            return res['_source']
        except exceptions.NotFoundError as error:
            log.error(error)
            return None

    def get_instance_by_fqdn(self, fqdn):
        q = Search(using=self.conn, index=self.db_name,
                   doc_type=self.doc_type) \
            .query('match', PublicDnsName=fqdn)

        try:
            res = q.execute()
            instance_id = res.hits.hits[0]['_source']['InstanceId']
            return self.get_instance_by_id(doc_id=instance_id)
        except exceptions.NotFoundError as error:
            log.error(error)
            return None

    def get_all_match(self, query_str):
        q = Search(using=self.conn, index=self.db_name,
                   doc_type=self.doc_type) \
            .query('match', _all=query_str)

        try:
            res = q.execute()
            return res
        except exceptions.NotFoundError as error:
            log.error(error)
            return None

    def get_elbs_by_instanceid(self, instance_id):
        q = Search(using=self.conn, index=self.db_name,
                   doc_type='aws_elb') \
            .query('nested',
                   path='Instances',
                   query=Q('bool',
                           must=[Q('match',
                                   **{'Instances.InstanceId': instance_id})]
                           )
                   )

        try:
            res = q.execute()
            return res
        except exceptions.NotFoundError as error:
            log.error(error)
            return None

    def get_route53_dns_by_name(self, fqdn):
        q = Search(using=self.conn, index=self.db_name,
                   doc_type='aws_route53') \
            .query('nested',
                   path='ResourceRecords',
                   query=Q('bool',
                           must=[Q('match',
                                   **{'ResourceRecords.Value': fqdn})]
                           )
                   )

        try:
            res = q.execute()
            return res
        except exceptions.NotFoundError as error:
            log.error(error)
            return None

    def get_endpoint_by_name(self, fqdn):
        q = Search(using=self.conn, index=self.db_name,
                   doc_type="ultradns") \
            .query('match', _all=fqdn)

        try:
            res = q.execute()
            return res.hits[0]
        except exceptions.NotFoundError as error:
            log.error(error)
            return None
