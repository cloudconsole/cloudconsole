#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3

import config
from config import log
from storage import writer


class Ec2(object):
    """Ec2 connection object"""

    def __init__(self, region):
        super(Ec2, self).__init__()
        self.region = region
        self.pg_size = config.CRAWLER_PAGE_SIZE

        self.conn = boto3.client('ec2', region_name=self.region)

    def crawl_all_instance(self):
        paginator = self.conn.get_paginator('describe_instances')

        for page in paginator.paginate(
                PaginationConfig={'PageSize': self.pg_size}):
            for result in page['Reservations']:
                writer.put(docs=result['Instances'], doc_type='ec2')
            log.info("Indexed %d Instances" % self.pg_size)


class Elb(object):
    """Ebs connection object"""

    def __init__(self, region):
        super(Elb, self).__init__()
        self.arg = region
        self.pg_size = 100

        self.conn = boto3.client('elb')

    def crawl_all_elb(self):
        paginator = self.conn.get_paginator('describe_load_balancers')

        for page in paginator.paginate(
                PaginationConfig={'PageSize': self.pg_size}):
            writer.put(docs=page['LoadBalancerDescriptions'],
                       doc_type='elb')
            log.info("Indexed %d ELBs" % self.pg_size)
