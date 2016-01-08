import boto3
import elasticsearch
from flask import request

from cloudconsole import app
from cloudconsole.helpers import render_page
from storage import reader

es = elasticsearch.Elasticsearch()
ec2_client = boto3.client('ec2')


@app.route('/')
def dashboard():
    return render_page(template='dashboard.html', page_data="Dashboard")


@app.route('/settings')
def settings():
    return render_page(template='dashboard.html', page_data="Settings")


@app.route('/search')
def search():
    search_query = request.args.get('search_query')
    resp = reader.get_all_match(query_str=search_query)

    return render_page(template='search-results.html',
                       query=search_query,
                       page_data=resp)


@app.route('/ec2/<search_query>')
def describe_instance(search_query):
    if search_query.startswith("ec2-"):
        resp = ec2_client.describe_instances(
            Filters=[{'Name': 'dns-name', 'Values': [search_query, ]}])

        return render_page(template='describe-instance.html',
                           query=search_query,
                           page_data=resp)
    elif search_query.startswith("i-"):
        resp = reader.get_doc(doc_type='ec2', doc_id=search_query)
        vars = {'elbs': reader.get_elbs_by_instance(instance_id=search_query)}

        return render_page(template='describe-instance.html',
                           query=search_query,
                           page_data=resp,
                           extra_vars=vars)
    else:
        resp = reader.get_all_match(doc_type='ec2', query_str=search_query)

        return render_page(template='describe-instances.html',
                           query=search_query,
                           page_data=resp)
