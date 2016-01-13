#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ultra_rest_client
from storage import driver
from config import log


class UltraDns(object):
    """Ultrdna connection object"""

    def __init__(self, username, password):
        super(UltraDns, self).__init__()
        self.username = username
        self.password = password
        self.use_http = False
        self.domain = 'restapi.ultradns.com'

        self.conn = ultra_rest_client.RestApiClient(self.username,
                                                    self.password,
                                                    self.use_http,
                                                    self.domain)
        self.zone_version = self.conn.version()
        self.acc_info = self.conn.get_account_details()
        self.acc_name = self.acc_info[u'accounts'][0][u'accountName']

        self.writer = driver.Writer(doc_type='ultradns')

    def crawl_all_zones(self):
        all_zones = self.conn.get_zones_of_account(self.acc_name)

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

                self.writer.put_docs(docs=records['rrSets'])
                log.info("Indexed %d ultradns records" % result_count )

                if result_count == records['resultInfo']['totalCount']:
                    paginate = False
