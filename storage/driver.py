#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import pymongo.errors

import config


class Writer(object):
    """Storage Reader Object"""

    def __init__(self, doc_type=None):
        super(Writer, self).__init__()
        self.db_name = config.db_name
        self.doc_type = doc_type

        # self.conn = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URI)
        self.conn = MongoClient(config.mongodb_uri)
        self.db = self.conn[self.db_name]

        self.coll = self.db[self.doc_type]

    def insert_many(self, docs):
        self.coll.insert_many(docs)

        success = True
        return success

    def insert_one(self, doc):
        self.coll.insert_one(doc)

        success = True
        return success

    def create_update_index(self):
        machines_index = [('ssh_key_name', 'text'),
                          ('type', 'text'),
                          ('public_dns', 'text'),
                          ('private_dns', 'text'),
                          ('tags', 'text'),
                          ('security_group', 'text')]
        try:
            res = self.coll.create_index(machines_index,
                                         name='machines_index',
                                         background=True)
        except pymongo.errors.OperationFailure as error:
            if error.code == 85:
                return True
            else:
                return False

    # def update_one(self, doc):
    #     old_doc = self.get_doc(doc_id=doc[self.id_identifier])
    #     print(old_doc)
    #     print(doc)
    #     # status = self.conn.update_one(index=self.db_name,
    #     #                           doc_type=self.doc_type,
    #     #                           id=doc[self.id_identifier],
    #     #                           body=doc)
    #     return True


class Reader(object):
    """Storage Reader Object"""

    def __init__(self, doc_type=None):
        super(Reader, self).__init__()
        self.db_name = config.db_name
        self.doc_type = doc_type

        self.conn = MongoClient(config.mongodb_uri)
        self.db = self.conn[self.db_name]

        self.coll = self.db[self.doc_type]

    def if_doc_exists(self, doc_id):
        return bool(self.coll.find_one({'_id': doc_id}))

    def find_docs(self, query):
        result = []
        for cur in self.coll.find(query):
            result.append(cur)

        return result

    def get_all_match(self, query_str):
        query = {'$text': {'$search': query_str}}
        return self.find_docs(query)

    def get_instance_by_id(self, doc_id):
        query = {'_id': doc_id}
        res = self.coll.find_one(query)

        return res

    def get_instance_by_fqdn(self, fqdn):
        query = {'public_dns': fqdn}
        return self.find_docs(query)

    def get_elbs_by_instanceid(self, instance_id):
        query = {'backends': instance_id}
        return self.find_docs(query)

    def get_dns_by_fqdn(self, fqdn):
        query = {'records': fqdn}
        return self.find_docs(query)
