#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import os.path
import uuid

import ultra_rest_client

from logger import log
from storage import driver


def get_credentials(username, password):
    cred_file = os.path.expanduser('~/.cloudconsole')

    if username and password:
        return username, password
    elif os.path.isfile(cred_file):
        config = configparser.ConfigParser()
        config.read(cred_file)
        username = config['ultradns']['username']
        password = config['ultradns']['password']

        return username, password


def prune_dns_fields(fdoc):
    """Extract only the required fields and discard the unwanted fields

    Args:
        fdoc (dict): Ultradns record set document

    Returns:
        dict: Filtered Ultradns document

    """
    doc = {
        '_id': str(uuid.uuid5(uuid.NAMESPACE_DNS,
                              fdoc['ownerName'].rstrip('.'))),
        'name': fdoc['ownerName'].rstrip('.'),
        'type': fdoc['rrtype'][:-4],
        'records': [],
        'cloud_provider': 'Ultradns'
    }

    if 'rdata' in fdoc:
        for rec in fdoc['rdata']:
            doc['records'].append(rec.rstrip('.'))

    return doc


class UltraDns(object):
    """Ultrdna connection object"""

    def __init__(self, username=None, password=None):
        super(UltraDns, self).__init__()
        self.username, self.password = get_credentials(username, password)
        self.use_http = False
        self.domain = 'restapi.ultradns.com'

        self.conn = ultra_rest_client.RestApiClient(self.username,
                                                    self.password,
                                                    self.use_http,
                                                    self.domain)
        self.zone_version = self.conn.version()
        self.acc_info = self.conn.get_account_details()
        self.acc_name = self.acc_info[u'accounts'][0][u'accountName']

        self.writer = driver.Writer(doc_type='dns')
        self.reader = driver.Reader(doc_type='dns')

    def crawl_all_zones(self):
        all_zones = self.conn.get_zones_of_account(self.acc_name)
        total_records = 0

        for zone in all_zones['zones']:
            zone_name = zone['properties']['name']

            query_offset = 0
            query_limit = 100
            result_count = 0
            paginate = True

            while paginate:
                records = self.conn.get_rrsets(zone_name,
                                               offset=query_offset,
                                               limit=query_limit)
                result_count += records['resultInfo']['returnedCount']
                query_offset += query_limit

                docs_to_add = []
                docs_to_update = []
                for doc in records['rrSets']:
                    if doc['rrtype'][:-4] == 'CNAME' or \
                                    doc['rrtype'][:-4] == 'A':
                        doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS,
                                                doc['ownerName'].rstrip('.')))
                        if self.reader.if_doc_exists(doc_id=doc_id):
                            docs_to_update.append(doc)
                        else:
                            docs_to_add.append(prune_dns_fields(fdoc=doc))

                if docs_to_add:
                    self.writer.insert_many(docs=docs_to_add)
                    total_records += len(docs_to_add)
                    log.dubug("Crawled %d ultradns records" % len(docs_to_add))

                if result_count == records['resultInfo']['totalCount']:
                    paginate = False

        log.info("Crawled %d ultradns records" % total_records)
