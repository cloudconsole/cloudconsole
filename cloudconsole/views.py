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
    reader = driver.Reader(doc_type='machines')
    resp = reader.get_all_match(query_str=search_query)

    return render_page(template='search-results.html',
                       query=search_query,
                       page_data=resp)


@app.route('/ec2/<search_query>')
def describe_instance(search_query):
    mreader = driver.Reader(doc_type='machines')
    lreader = driver.Reader(doc_type='loadbalancers')
    dreader = driver.Reader(doc_type='dns')

    extra_var = {}

    if search_query.startswith("ec2-"):
        resp = mreader.get_instance_by_fqdn(fqdn=search_query)
    elif search_query.startswith("i-"):
        resp = mreader.get_instance_by_id(doc_id=search_query)
    else:
        resp = mreader.get_all_match(query_str=search_query)

    if resp:
        instance_fqdn = resp['public_dns']

        extra_var['lbs'] = lreader.get_elbs_by_instanceid(
            instance_id=search_query)
        extra_var['dns'] = dreader.get_dns_by_fqdn(
            fqdn=instance_fqdn)

        if extra_var['lbs']:
            for elb in extra_var['lbs']:
                for cur in dreader.get_dns_by_fqdn(fqdn=elb['public_dns']):
                    extra_var['dns'].append(cur)

    return render_page(template='describe-instance.html',
                       query=search_query,
                       page_data=resp,
                       extra_vars=extra_var)
