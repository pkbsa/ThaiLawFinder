import csv
from io import StringIO, TextIOWrapper
from flask import Flask, jsonify, redirect, request, url_for
from flask import render_template
from elasticsearch import Elasticsearch
import math
import time


from flask import send_file
import mysql.connector

from features import converter
from features import content
from pythainlp.tokenize import word_tokenize
model_path = 'pythainlp_model/thai2vec.bin'

# from gensim.models import load_word2vec_format
# import fasttext

# model = load_word2vec_format(model_path, binary=True)

# from gensim.models import KeyedVectors
# model = KeyedVectors.load_word2vec_format(model_path,binary=True)
from pythainlp import word_vector
model = word_vector.WordVector(model_name="thai2fit_wv").get_model()
# ELASTIC_PASSWORD = ""

# existing_index_name = 'law-data-reindex-1'

# es = Elasticsearch("http://localhost:9200",
#                  http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

ELASTIC_PASSWORD = "ppfBW5a5bFGDw7W7v0QqgsdC"

existing_index_name = 'law-data-reindex'

es = Elasticsearch(['https://97652710d0b74c249f19a27b3ef4a111.ap-southeast-1.aws.found.io:443'], http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

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

def findSimilarity(sentence):
    cutedSentence = word_tokenize(sentence, engine='deepcut')
    # print('cutedSentence:', cutedSentence)
    choiceWord = []
    for i in cutedSentence:
        try:
            similar = model.most_similar_cosmul(positive=["คดี","กฎหมาย",i], negative=[])
        except:
            similar=[]
        count=0
        for l, k in similar:
            # print(l, k)
            if k > 0.22 and count <=3 and l not in choiceWord:
                choiceWord.append(l)
                count+=1
        # print("-----")
    # print("choiceWord", choiceWord)
    return choiceWord


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
    choiceWord = findSimilarity(keyword)
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
                        {'match': {'addtitional': keyword}},
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

    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total, choiceWord=choiceWord)


@app.route('/advanced-search')
def advancedSearch():
    page_size = 5
    keyword = request.args.get('keyword')
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
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM law")
    law_data = cursor.fetchall()
    db.close()

    codes = get_codes(es, existing_index_name)
    
    return render_template('admin-dashboard.html', codes=codes, law_data=law_data)

@app.route('/info/<name>')
def get_status(name):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM law WHERE name = %s", (name,))
    status = cursor.fetchone()
    db.close()
    return {'results': status}

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
        content.removeContent(code_to_delete)
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

        content.addContent(csv_data)

        return 'File uploaded and data inserted into database/elastic successfully'


@app.route('/download')
def download_file():
    return send_file('static/output.csv', as_attachment=True)
