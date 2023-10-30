from flask import Flask, request, render_template
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

    # Search the first Elasticsearch index
    body1 = {
        'size': page_size,
        'from': page_size * (page_no - 1),
        'query': {
            "bool": {
                "should": [
                    {"match": {"Detail": keyword}}
                ]
            }
        }
    }
    res1 = es.search(index='200-law-test-after', doc_type='', body=body1)
    hits1 = [{'Title': doc['_source']['Title'], 'Detail': doc['_source']['Detail']} for doc in res1['hits']['hits']]
    page_total1 = math.ceil(res1['hits']['total']['value'] / page_size)

    # Search the second Elasticsearch index
    body2 = {
        'query': {
            "bool": {
                "should": [
                    { "match": { "code": keyword }},
                    { "match": { "section": keyword }},
                    { "match": { "title": keyword }},
                    { "match": { "chapter": keyword }},
                    { "match": { "part": keyword }},
                    { "match": { "addtitional": keyword }},
                    { "match": { "detail": keyword }}
                ]
            }
        }
    }
    res2 = es.search(index='test-law-2', doc_type='', body=body2)
    hits2 = [{'code': doc['_source']['code'], 'section': doc['_source']['section'],
              'title': doc['_source']['title'], 'chapter': doc['_source']['chapter'],
              'part': doc['_source']['part'], 'addtitional': doc['_source']['addtitional'],
              'detail': doc['_source']['detail'] } for doc in res2['hits']['hits']]

    return render_template('search.html', keyword=keyword, hits1=hits1, hits2=hits2, page_no=page_no, page_total=page_total1)

if __name__ == "__main__":
    app.run(debug=True)