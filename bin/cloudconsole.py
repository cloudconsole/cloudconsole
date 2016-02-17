#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

import config
from crawler import aws
from crawler import ultradns
from logger import log


def get_cmd_parser():
    parser = argparse.ArgumentParser(
            description='Cloud Config cli tool',
            epilog='Author ashokraja.r@gmail.com | Feedback most welcomed,'
                   'even better a pull request.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version',
                        version='%(prog)s 1.0.dev1')

    parser.add_argument('runcrawler',
                        help='Starts to crawl your infrastructure.')

    return parser.parse_args()


def crawl_aws():
    log.info("AWS ec2 crawler started")
    for region in config.regions:
        log.info("AWS ec2 crawler : crawling region=%s" % region)
        ec2 = aws.Ec2(region=region)
        ec2.crawl_all_instance()
    log.info("AWS ec2 crawler finished")

    log.info("AWS elb crawler started")
    for region in config.regions:
        log.info("AWS elb crawler : crawling region=%s" % region)
        elb = aws.Elb(region=region)
        elb.crawl_all_elb()
    log.info("AWS elb crawler finished")

    log.info("AWS route53 crawler started")
    elb = aws.Route53()
    elb.crawl_all_zones()
    log.info("AWS route53 crawler finished")


def crawl_ultradns():
    log.info("Ultra DNS crawler started")
    dns = ultradns.UltraDns()
    dns.crawl_all_zones()
    log.info("Ultra DNS crawler finished")


def runcrawler_main():

    if config.enabled_services['aws']:
        crawl_aws()

    if config.enabled_services['ultradns']:
        crawl_ultradns()

if __name__ == '__main__':
    args = get_cmd_parser()

    if args.runcrawler:
        runcrawler_main()
