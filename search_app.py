import csv
from io import StringIO, TextIOWrapper
from flask import Flask, jsonify, redirect, request, url_for
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
import math

ELASTIC_PASSWORD = ""
existing_index_name = 'law-data-reindex-1'

es = Elasticsearch("http://localhost:9200",
                   http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    page_size = 5
    keyword = request.args.get('keyword')
    page_no = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'section')
    order = request.args.get('order', 'asc')

    if not keyword.strip() :
        body = {
            'size': page_size,
            'from': page_size * (page_no - 1),
            'query': {
                'match_all': {}
            }
        }

    else:
        body = {
            'size': page_size,
            'from': page_size * (page_no - 1),
            'query': {
                'bool': {
                    'should': [
                        {'match': {'code': {'query': keyword, 'boost': 1.5}}},  
                        {'match': {'section': {'query': keyword, 'boost': 2.0}}},
                        {'match': {'book': keyword}},
                        {'match': {'title': keyword}},
                        {'match': {'chapter': keyword}},
                        {'match': {'part': keyword}},
                        {'match': {'additional': keyword}},
                        {'match': {'detail': keyword}}
                    ]
                }
            }
        }

    if sort == 'code':
        body['sort'] = [{'section_sort': {'order': order}}]

    res = es.search(index=existing_index_name, doc_type='', body=body)
    hits = [{'code': doc['_source']['code'], 'section': doc['_source']['section'],
             'book': doc['_source']['book'],
             'title': doc['_source']['title'], 'chapter': doc['_source']['chapter'],
             'part': doc['_source']['part'], 'addtitional': doc['_source']['addtitional'],
             'detail': doc['_source']['detail']} for doc in res['hits']['hits']]

    page_total = math.ceil(res['hits']['total']['value'] / page_size)

    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)


@app.route('/advanced-search')
def advancedSearch():
    page_size = 5
    section = request.args.get('section')
    code = request.args.get('code')
    book = request.args.get('book')
    title = request.args.get('title')
    chapter = request.args.get('chapter')
    sort = request.args.get('sort', 'section')
    order = request.args.get('order', 'asc')
    hits = []
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    should_conditions = []
    print(code)
    

    if code and code.strip():  
        should_conditions.append({"match_phrase": {"code": code}})
    else :
        should_conditions.append({"match_all": {}})

    if book and book.strip() and book != 'None' and book != '-':
        should_conditions.append({"match": {"book": book}})
    if title and title.strip() and title != 'None' and title != '-':
        should_conditions.append({"match": {"title": title}})
    if chapter and chapter.strip() and chapter != 'None' and chapter != '-':
        should_conditions.append({"match_phrase": {"chapter": chapter}})
    if section:
        should_conditions.append({"match": {"section": section}})

    print(should_conditions)

    if should_conditions:
       
        body = {
            'size': page_size,
            'from': page_size * (page_no - 1),
            'query': {
                "bool": {
                    "must": should_conditions
                }
            }
        }

        if sort == 'code':
            body['sort'] = [{'section_sort': {'order': order}}]
        

        res = es.search(index=existing_index_name, doc_type='', body=body)
        hits = [{'code': doc['_source']['code'], 'section': doc['_source']['section'],
                 'book': doc['_source']['book'],
                'title': doc['_source']['title'], 'chapter': doc['_source']['chapter'],
                 'part': doc['_source']['part'], 'addtitional': doc['_source']['addtitional'],
                 'detail': doc['_source']['detail']} for doc in res['hits']['hits']]

        page_total = math.ceil(res['hits']['total']['value'] / page_size)

        return render_template('advanced-search.html', code=code, book=book, title=title, chapter=chapter, hits=hits, page_no=page_no, page_total=page_total)
    else:
        return render_template('advanced-search.html', code=code, book=book, title=title, chapter=chapter, hits=hits, page_no=page_no, page_total=page_total)


def get_codes(es, index_name):
    # Get unique codes from the Elasticsearch index
    result = es.search(index=index_name, size=0, body={"aggs": {"codes": {"terms": {"field": "code.raw"}}}})
    codes = [{"key": bucket['key'], "doc_count": bucket['doc_count']} for bucket in result['aggregations']['codes']['buckets']]
    return codes


@app.route('/dashboard')
def dashboard():
    # Get unique categories for visualization
    codes = get_codes(es, existing_index_name)
    
    return render_template('dashboard.html', codes=codes)

@app.route('/dashboard-csv')
def dashboardCSV():
    return render_template('dashboard-csv.html')

@app.route('/dashboard-html')
def dashboardHTML():
    return render_template('dashboard-html.html')

def delete_data_by_code(es, index_name, code):
    es.delete_by_query(index=index_name, body={"query": {"match": {"code.raw": code}}})

@app.route('/delete', methods=['POST'])
def delete_data():
    try:
        code_to_delete = request.form.get('code')
        delete_data_by_code(es, existing_index_name, code_to_delete)
        return redirect(url_for('dashboard'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def add_csv_to_index(es, index_name, csv_data):
    # Assuming the CSV file has a header row
    reader = csv.DictReader(StringIO(csv_data))
    
    # Bulk index the CSV data into Elasticsearch
    documents = []

    for row in reader:
        document = {
            'code': row['code'],
            'section': row['section'],
            'book': row['book'],
            'title': row['title'],
            'chapter': row['chapter'],
            'part': row['part'],
            'addtitional': row['addtitional'],
            'detail': row['detail'],
            'section_sort': row['section_sort']
            # Add more fields as needed
        }
       
        es.index(index=index_name, doc_type='_doc', body=document)
        
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    try:
        # Get the uploaded file from the form
        uploaded_file = request.files['file']

        # Read the CSV file content
        csv_data = uploaded_file.stream.read().decode('utf-8')

        # Add CSV data to the existing Elasticsearch index
        add_csv_to_index(es, existing_index_name, csv_data)

        # Redirect to the dashboard page after uploading
        return redirect(url_for('dashboard'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
