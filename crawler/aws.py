#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3

import config
from config import log
from storage import driver


class Ec2(object):
    """Ec2 connection object"""

    def __init__(self, region):
        super(Ec2, self).__init__()
        self.region = region
        self.pg_size = config.CRAWLER_PAGE_SIZE

        self.conn = boto3.client('ec2', region_name=self.region)
        self.writer = driver.Writer(doc_type='aws_ec2')

    def crawl_all_instance(self):
        paginator = self.conn.get_paginator('describe_instances')

        for page in paginator.paginate(
                PaginationConfig={'PageSize': self.pg_size}):
            for result in page['Reservations']:
                self.writer.put_docs(docs=result['Instances'])
            log.info("Indexed %d Instances" % self.pg_size)


class Elb(object):
    """Ebs connection object"""

    def __init__(self, region):
        super(Elb, self).__init__()
        self.arg = region
        self.pg_size = 100

        self.conn = boto3.client('elb')
        self.writer = driver.Writer(doc_type='aws_elb')

    def crawl_all_elb(self):
        paginator = self.conn.get_paginator('describe_load_balancers')

        for page in paginator.paginate(
                PaginationConfig={'PageSize': self.pg_size}):
            self.writer.put_docs(docs=page['LoadBalancerDescriptions'])
            log.info("Indexed %d ELBs" % self.pg_size)


class Route53(object):
    """Route 53 connection object"""

    def __init__(self):
        super(Route53, self).__init__()
        self.pg_size = 100

        self.conn = boto3.client('route53')
        self.writer = driver.Writer(doc_type='aws_route53')

    def crawl_all_zones(self):
        zones = []

        paginator = self.conn.get_paginator('list_hosted_zones')
        for page in paginator.paginate(
                PaginationConfig={'MaxItems': self.pg_size}):
            for zone in page['HostedZones']:
                zones.append(zone['Id'])

        paginator = self.conn.get_paginator('list_resource_record_sets')
        for zone in zones:
            for page in paginator.paginate(
                    HostedZoneId=zone,
                    PaginationConfig={'MaxItems': self.pg_size}):
                self.writer.put_docs(docs=page['ResourceRecordSets'])
                log.info("Indexed %d route53 entries" % self.pg_size)
