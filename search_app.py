import csv
from io import StringIO, TextIOWrapper
from flask import Flask, jsonify, redirect, request, url_for
from flask import render_template
from elasticsearch import Elasticsearch
import math
import time
import json

from flask import send_file
import mysql.connector

from features import converter, tableofcontent, word_advisor

ELASTIC_PASSWORD = ""

es = Elasticsearch("http://localhost:9200",
                 http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

# ELASTIC_PASSWORD = "ppfBW5a5bFGDw7W7v0QqgsdC"

# es = Elasticsearch(['https://97652710d0b74c249f19a27b3ef4a111.ap-southeast-1.aws.found.io:443'], http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

existing_index_name = 'law-data-reindex'

with open('config.json', 'r') as f:
    config = json.load(f)

BASIC_SEARCH_BOOST_CODE = config['BASIC_SEARCH_BOOST_CODE']
BASIC_SEARCH_BOOST_SECTION = config['BASIC_SEARCH_BOOST_SECTION']
BASIC_SEARCH_BOOST_BOOK = config['BASIC_SEARCH_BOOST_BOOK']
BASIC_SEARCH_BOOST_TITLE = config['BASIC_SEARCH_BOOST_TITLE']
BASIC_SEARCH_BOOST_CHAPTER = config['BASIC_SEARCH_BOOST_CHAPTER']
BASIC_SEARCH_BOOST_PART = config['BASIC_SEARCH_BOOST_PART']
BASIC_SEARCH_BOOST_DETAIL = config['BASIC_SEARCH_BOOST_DETAIL']


app = Flask(__name__)

# def connect_to_db():
#     db = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="thailawfinder"
#     )
#     return db

def connect_to_db():
    db = mysql.connector.connect(
        host="db4free.net",
        user="netgluayadmin",
        password="netgluay",
        database="netgluaydb"
    )
    return db


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM law")
    law_data = cursor.fetchall()
    db.close()    
    return render_template('docs.html', rows=law_data)


@app.route('/search')
def search():
    page_size = 5
    keyword = request.args.get('keyword')
    page_no = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'section')
    order = request.args.get('order', 'asc')

    advised_word = word_advisor.findSimilarity(keyword)

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
                        {'match': {'code': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_CODE}}},  
                        {'match': {'section': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_SECTION}}},
                        {'match': {'book': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_BOOK}}},
                        {'match': {'title': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_TITLE}}},
                        {'match': {'chapter': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_CHAPTER}}},
                        {'match': {'part': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_PART}}},
                        {'match': {'addtitional': keyword}},
                        {'match': {'detail': {'query': keyword, 'boost': BASIC_SEARCH_BOOST_DETAIL}}}
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

    total_hits = res['hits']['total']['value']  # Calculate total hits
    page_total = math.ceil(res['hits']['total']['value'] / page_size)

    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total, total_hits=total_hits, advised_word=advised_word)


@app.route('/parametric-search')
def parametricSearch():
    page_size = 5
    keyword = ""
    advised_word = []

    if request.args.get('keyword'):
        keyword = request.args.get('keyword') 
        advised_word = word_advisor.findSimilarity(keyword)

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

    if keyword and keyword.strip(): 
        should_conditions.append({"match": {"detail": keyword}})

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
        
        total_hits = res['hits']['total']['value']  # Calculate total hits

        page_total = math.ceil(res['hits']['total']['value'] / page_size)

        return render_template('parametric-search.html', code=code, book=book, title=title, chapter=chapter, hits=hits, page_no=page_no, page_total=page_total, keyword=keyword, total_hits=total_hits, advised_word=advised_word)
    else:
        return render_template('parametric-search.html', code=code, book=book, title=title, chapter=chapter, hits=hits, page_no=page_no, page_total=page_total, keyword=keyword, total_hits=0, advised_word=advised_word)

def get_codes(es, index_name):
    # Get unique codes from the Elasticsearch index
    result = es.search(index=index_name, size=0, body={"aggs": {"codes": {"terms": {"field": "code.raw", "size": 10000}}}})
    codes = [{"key": bucket['key'], "doc_count": bucket['doc_count']} for bucket in result['aggregations']['codes']['buckets']]
    return codes

@app.route('/dashboard')
def dashboard():
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM law")
    law_data = cursor.fetchall()
    db.close()

    codes = get_codes(es, existing_index_name)
    
    return render_template('admin-dashboard.html', codes=codes, law_data=law_data, config_setting=config)

@app.route('/admin-convert')
def dashboardHTML():
    return render_template('admin-convert.html')

@app.route('/admin-upload')
def dashboardCSV():
    return render_template('admin-upload.html')

def delete_data_by_code(es, index_name, code):
    es.delete_by_query(index=index_name, body={"query": {"match": {"code.raw": code}}})

@app.route('/delete', methods=['POST'])
def delete_data():
    try:
        code_to_delete = request.form.get('code')
        delete_data_by_code(es, existing_index_name, code_to_delete)
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM law WHERE name = %s", (code_to_delete,))
        db.commit() 
        db.close()
        tableofcontent.removeContent(code_to_delete)
        time.sleep(1)

        return redirect(url_for('dashboard'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def add_csv_to_index(es, index_name, csv_data):
    reader = csv.DictReader(StringIO(csv_data))
    if csv_data.startswith('\ufeff'):
        csv_data = csv_data[1:]
    
    reader = csv.DictReader(StringIO(csv_data))
    
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
        }
       
        es.index(index=index_name, doc_type='_doc', body=document)

@app.route('/convert', methods=['POST'])
def convert_txt_to_csv():
    code = request.form.get('code')
    file = request.files['file']
    file.save('static/input.txt')
    converter.process_file(code)  
    return 'File processed successfully', 200

@app.route('/upload', methods=['POST'])
def upload_csv():
    if request.method == 'POST':
        name = request.form['name']
        copy = request.form['copy']
        status = request.form['status']
        date = request.form['date']
        url = request.form['url']
        currentStatus = 1
        
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO law (name, copy, status, date, url, currentStatus) VALUES (%s, %s, %s, %s, %s, %s)", (name, copy, status, date, url, currentStatus))
        db.commit()

        # Check if the data was inserted successfully
        if cursor.rowcount == 0:
            db.close()
            print('Error: Data was not inserted into database')
            return 'Error: Data was not inserted into database'
        else:
            print('Data inserted into database successfully')

        db.close()

        uploaded_file = request.files['file']
        csv_data = uploaded_file.stream.read().decode('utf-8')
        add_csv_to_index(es, existing_index_name, csv_data)

        tableofcontent.addContent(csv_data)

        return 'File uploaded and data inserted into database/elastic successfully'

@app.route('/upload-elastic', methods=['POST'])
def upload_to_elastic_only():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        csv_data = uploaded_file.stream.read().decode('utf-8')
        add_csv_to_index(es, existing_index_name, csv_data)
    return 'File uploaded and data inserted into database/elastic successfully'

@app.route('/delete-elastic', methods=['POST'])
def delete_from_elastic():
    try:
        code_to_delete = request.form.get('code')
        delete_data_by_code(es, existing_index_name, code_to_delete)
        time.sleep(1)

        return redirect(url_for('dashboard'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download')
def download_file():
    return send_file('static/output.csv', as_attachment=True)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')

