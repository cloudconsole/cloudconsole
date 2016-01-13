#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request

from cloudconsole import app
from cloudconsole.helpers import render_page
from storage import driver


@app.route('/')
def dashboard():
    return render_page(template='dashboard.html', page_data="Dashboard")


@app.route('/settings')
def settings():
    return render_page(template='dashboard.html', page_data="Settings")


@app.route('/search')
def search():
    search_query = request.args.get('search_query')
    reader = driver.Reader()
    resp = reader.get_all_match(query_str=search_query)

    return render_page(template='search-results.html',
                       query=search_query,
                       page_data=resp)


@app.route('/ec2/<search_query>')
def describe_instance(search_query):
    reader = driver.Reader(doc_type='aws_ec2')
    extra_var = {}

    if search_query.startswith("ec2-"):
        resp = reader.get_instance_by_fqdn(fqdn=search_query)
    elif search_query.startswith("i-"):
        resp = reader.get_instance_by_id(doc_id=search_query)
    else:
        resp = reader.get_all_match(query_str=search_query)

    instance_fqdn = resp['PublicDnsName']

    extra_var['elbs'] = reader.get_elbs_by_instanceid(instance_id=search_query)
    extra_var['route53'] = reader.get_route53_dns_by_name(fqdn=instance_fqdn)
    extra_var['ultradns'] = [reader.get_endpoint_by_name(fqdn=instance_fqdn)]

    if extra_var['elbs']:
        for elb in extra_var['elbs']:
            res = reader.get_endpoint_by_name(fqdn=elb.DNSName)
            if res:
                extra_var['ultradns'].append(res)

    return render_page(template='describe-instance.html',
                       query=search_query,
                       page_data=resp,
                       extra_vars=extra_var)
