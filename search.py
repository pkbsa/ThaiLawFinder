from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
import math

ELASTIC_PASSWORD = ""

es = Elasticsearch("http://localhost:9200",
                   http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword')
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no - 1),
        'query': {
            "bool": {
                "should": [
                    { "match": { "Detail": keyword }}               
                ]
            }
        }
    }

    res = es.search(index='200-law-test-after', doc_type='', body=body)
    hits = [{'Title': doc['_source']['Title'], 'Detail': doc['_source']['Detail']} for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value']/page_size)
    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)
