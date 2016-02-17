#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3

import config
from logger import log
from storage import driver


def prune_ec2_fields(fdoc):
    """Extract only the required fields and discard the unwanted fields

    Args:
        fdoc (dict): AWS Ec2 Instance document

    Returns:
        dict: Filtered AWS Ec2 Instance document

    """
    doc = {
        '_id': fdoc['InstanceId'],
        'state': fdoc['State']['Name'],
        'virtualization': fdoc['VirtualizationType'],
        'arch': fdoc['Architecture'],
        'root_device': fdoc['RootDeviceType'],
        'type': fdoc['InstanceType'],
        'data_center': fdoc['Placement']['AvailabilityZone'],
        'security_group': [],
        'cloud_provider': 'Amazon'
    }

    for grp in fdoc['SecurityGroups']:
        doc['security_group'].append(grp['GroupName'])

    if 'KeyName' in fdoc:
        doc['ssh_key_name'] = fdoc['KeyName']

    if 'Tags' in fdoc:
        doc['tags'] = fdoc['Tags']

    if 'IamInstanceProfile' in fdoc:
        doc['iam_profile'] = fdoc['IamInstanceProfile']

    if 'LaunchTime' in fdoc:
        doc['launch_time'] = fdoc['LaunchTime']

    if 'PublicDnsName' in fdoc:
        doc['public_dns'] = fdoc['PublicDnsName']

    if 'PrivateDnsName' in fdoc:
        doc['private_dns'] = fdoc['PrivateDnsName']

    if 'PublicIpAddress' in fdoc:
        doc['public_ip'] = fdoc['PublicIpAddress']

    if 'PrivateIpAddress' in fdoc:
        doc['private_ip'] = fdoc['PrivateIpAddress']

    return doc


def prune_elb_fields(fdoc):
    """Extract only the required fields and discard the unwanted fields

    Args:
        fdoc (dict): AWS ELB Instance document

    Returns:
        dict: Filtered AWS ELB Instance document

    """
    doc = {
        '_id': fdoc['LoadBalancerName'],
        'name': fdoc['LoadBalancerName'],
        'launch_time': fdoc['CreatedTime'],
        'data_center': ['AvailabilityZone'],
        'public_dns': fdoc['DNSName'],
        'cloud_provider': 'Amazon'
    }

    if fdoc['Instances']:
        doc['backends'] = []
        for instance in fdoc['Instances']:
            doc['backends'].append(instance['InstanceId'])

    return doc


def prune_dns_fields(fdoc):
    """Extract only the required fields and discard the unwanted fields

    Args:
        fdoc (dict): AWS Route53 document

    Returns:
        dict: Filtered AWS Route53 document

    """
    doc = {
        '_id': fdoc['Name'].rstrip('.'),
        'name': fdoc['Name'].rstrip('.'),
        'type': fdoc['Type'],
        'records': [],
        'cloud_provider': 'Amazon'
    }

    if 'ResourceRecords' in fdoc:
        for rec in fdoc['ResourceRecords']:
            doc['records'].append(rec['Value'].rstrip('.'))

    if 'AliasTarget' in fdoc:
        doc['records'].append(fdoc['AliasTarget']['DNSName'])

    return doc


def check_dns_record_exists(fdocs, new_doc):
    """Checks of the document already exists in the list

    Args:
        fdocs (list): List of AWS Route53 document
        new_doc (dict): AWS Route53 document

    Returns:
        bool: True if successful, False otherwise.
    """
    exists = False
    for fdoc in fdocs:
        if new_doc['_id'] == fdoc['_id']:
            exists = True
            break

    return exists


def merge_dns_docs(fdocs, dup_docs):
    """Merge the redundant/duplicate document records

    Args:
        fdocs (list): List of AWS Route53 document
        dup_docs (list): List if AWS Route53 duplicate document

    Returns:
        list: List of merged AWS Route53 document

    """
    docs = []

    for ddoc in dup_docs:
        for fdoc in fdocs:
            if ddoc['_id'] == fdoc['_id']:
                mod_doc = fdoc
                mod_doc['records'].append(ddoc['records'])
                docs.append(mod_doc)
                break
            else:
                docs.append(fdoc)

    return docs


class Ec2(object):
    """Ec2 connection object"""

    def __init__(self, region='us-east-1'):
        super(Ec2, self).__init__()
        self.region = region
        self.pg_size = config.crawler_page_size

        self.conn = boto3.client('ec2', region_name=self.region)
        self.writer = driver.Writer(doc_type='machines')
        self.reader = driver.Reader(doc_type='machines')

    def crawl_all_instance(self):
        paginator = self.conn.get_paginator('describe_instances')
        total_instances = 0

        for page in paginator.paginate(
                PaginationConfig={'PageSize': self.pg_size}):
            docs_to_add = []
            docs_to_update = []
            for result in page['Reservations']:
                for doc in result['Instances']:
                    # Ignore spot instances
                    if 'InstanceLifecycle' not in doc:
                        if self.reader.if_doc_exists(doc_id=doc['InstanceId']):
                            docs_to_update.append(prune_ec2_fields(fdoc=doc))
                        elif doc['State']['Name'] == 'running':
                            docs_to_add.append(prune_ec2_fields(fdoc=doc))

            if docs_to_add:
                self.writer.insert_many(docs=docs_to_add)
                total_instances += len(docs_to_add)
                log.debug("Crawled %d Instances" % len(docs_to_add))

        log.info("Crawled %d Instances" % total_instances)
        self.writer.create_update_index()
        log.info("Created Index for collection => machines")


class Elb(object):
    """Ebs connection object"""

    def __init__(self, region='us-east-1'):
        super(Elb, self).__init__()
        self.arg = region
        self.pg_size = 100

        self.conn = boto3.client('elb')
        self.writer = driver.Writer(doc_type='loadbalancers')
        self.reader = driver.Reader(doc_type='loadbalancers')

    def crawl_all_elb(self):
        paginator = self.conn.get_paginator('describe_load_balancers')
        total_elb = 0

        for page in paginator.paginate(
                PaginationConfig={'PageSize': self.pg_size}):
            docs_to_add = []
            docs_to_update = []
            for doc in page['LoadBalancerDescriptions']:
                if self.reader.if_doc_exists(doc_id=doc['LoadBalancerName']):
                    docs_to_update.append(prune_elb_fields(fdoc=doc))
                else:
                    docs_to_add.append(prune_elb_fields(fdoc=doc))

            if docs_to_add:
                self.writer.insert_many(docs=docs_to_add)
                total_elb += len(docs_to_add)
                log.debug("Crawled %d Load Balancers" % len(docs_to_add))

        log.info("Crawled %d Load Balancers" % total_elb)


class Route53(object):
    """Route 53 connection object"""

    def __init__(self):
        super(Route53, self).__init__()
        self.pg_size = 50

        self.conn = boto3.client('route53')
        self.writer = driver.Writer(doc_type='dns')
        self.reader = driver.Reader(doc_type='dns')

    def crawl_all_zones(self):
        zones = []
        total_records = 0

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
                docs_to_add = []
                docs_to_update = []
                dup_docs = []
                for doc in page['ResourceRecordSets']:
                    if doc['Type'] == 'CNAME' or doc['Type'] == 'A':
                        new_doc = prune_dns_fields(fdoc=doc)
                        doc_id = doc['Name'].rstrip('.')
                        if self.reader.if_doc_exists(doc_id=doc_id):
                            docs_to_update.append(new_doc)
                        else:
                            if docs_to_add:
                                if not check_dns_record_exists(
                                        docs_to_add, new_doc):
                                    docs_to_add.append(new_doc)
                                else:
                                    dup_docs.append(new_doc)
                            else:
                                docs_to_add.append(new_doc)

                if dup_docs:
                    docs_to_write = merge_dns_docs(docs_to_add, dup_docs)
                else:
                    docs_to_write = docs_to_add

                if docs_to_write:
                    self.writer.insert_many(docs=docs_to_add)
                    total_records += len(docs_to_write)
                    log.debug("Crawled %d route53 entries" % len(docs_to_write))

        log.info("Crawled %d route53 records" % total_records)
