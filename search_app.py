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

    # Default to sorting by 'section'
    if request.args.get('sort') != 'code':
        body = {
            'size': page_size,
            'from': page_size * (page_no - 1),
            'query': {
                "bool": {
                    "should": [
                        {"match": {"code": keyword}},
                        {"match": {"section": keyword}},
                        {"match": {"book": keyword}},
                        {"match": {"title": keyword}},
                        {"match": {"chapter": keyword}},
                        {"match": {"part": keyword}},
                        {"match": {"addtitional": keyword}},
                        {"match": {"detail": keyword}}
                    ]
                }
            }
        }
    else:
        if request.args.get('order') == 'asc':
            body = {
                'size': page_size,
                'from': page_size * (page_no - 1),
                'query': {
                    "bool": {
                        "should": [
                            {"match": {"code": keyword}},
                            {"match": {"section": keyword}},
                            {"match": {"book": keyword}},
                            {"match": {"title": keyword}},
                            {"match": {"chapter": keyword}},
                            {"match": {"part": keyword}},
                            {"match": {"addtitional": keyword}},
                            {"match": {"detail": keyword}}
                        ]
                    }
                },
                "sort": [
                    {'section_sort': {"order": "asc"}}
                ]
            }
        else:
             body = {
                'size': page_size,
                'from': page_size * (page_no - 1),
                'query': {
                    "bool": {
                        "should": [
                            {"match": {"code": keyword}},
                            {"match": {"section": keyword}},
                            {"match": {"book": keyword}},
                            {"match": {"title": keyword}},
                            {"match": {"chapter": keyword}},
                            {"match": {"part": keyword}},
                            {"match": {"addtitional": keyword}},
                            {"match": {"detail": keyword}}
                        ]
                    }
                },
                "sort": [
                    {'section_sort': {"order": "desc"}}
                ]
            }

    res = es.search(index='law-last-reindex-1', doc_type='', body=body)
    hits = [{'code': doc['_source']['code'], 'section': doc['_source']['section'],
             'book': doc['_source']['book'],
             'title': doc['_source']['title'], 'chapter': doc['_source']['chapter'],
             'part': doc['_source']['part'], 'addtitional': doc['_source']['addtitional'],
             'detail': doc['_source']['detail']} for doc in res['hits']['hits']]

    page_total = math.ceil(res['hits']['total']['value'] / page_size)

    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)


@app.route('/advanced-search')
def advancedSearch():
    page_size = 10
    section = request.args.get('section')
    code = request.args.get('code')
    book = request.args.get('book') 
    title = request.args.get('title')
    chapter = request.args.get('chapter')
    sort = request.args.get('sort')
    hits = []
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1


    should_conditions = []

    if code and code.strip():  # Check if code is not empty or just whitespace
        should_conditions.append({"match_phrase": {"code": code}})
    if book and book.strip() and book != 'None' and book != '-':  # Check if book is not empty or just whitespace
        should_conditions.append({"match": {"book": book}})
    if title and title.strip() and title != 'None' and title != '-':  # Check if title is not empty or just whitespace
        should_conditions.append({"match": {"title": title}})
    if chapter and chapter.strip() and chapter != 'None' and chapter != '-':  # Check if chapter is not empty or just whitespace
        should_conditions.append({"match_phrase": {"chapter": chapter}})
    if section:
        should_conditions.append({"match": {"section": section}})

            
    print(should_conditions)
    # Check if any conditions are provided
    if should_conditions:
        if sort != 'code':
            body={
                'size': page_size,
                'from': page_size * (page_no - 1),
                'query': {
                    "bool": {
                        "must": should_conditions
                    }
                }
            }
        else :
            if request.args.get('order') == 'asc':
                body={
                    'size': page_size,
                    'from': page_size * (page_no - 1),
                    'query': {
                        "bool": {
                            "must": should_conditions
                            }
                        },
                    "sort": [
                        {'section_sort': {"order": "asc"}}
                    ]
                }
            else:
                body={
                    'size': page_size,
                    'from': page_size * (page_no - 1),
                    'query': {
                        "bool": {
                            "must": should_conditions
                            }
                        },
                    "sort": [
                        {'section_sort': {"order": "desc"}}
                    ]
                }

        res=es.search(index='law-last-reindex-1', doc_type='', body=body)
        hits=[{'code': doc['_source']['code'], 'section': doc['_source']['section'],
                 'book': doc['_source']['book'],
                 'title': doc['_source']['title'], 'chapter': doc['_source']['chapter'],
                 'part': doc['_source']['part'], 'addtitional': doc['_source']['addtitional'],
                 'detail': doc['_source']['detail']} for doc in res['hits']['hits']]

        page_total=math.ceil(res['hits']['total']['value'] / page_size)

        return render_template('advanced-search.html',code=code,book=book,title=title,chapter=chapter,hits=hits, page_no=page_no, page_total=page_total)
    else:
        # Handle case when no search conditions are provided
        return render_template('advanced-search.html',code=code,book=book,title=title,chapter=chapter,hits=hits, page_no=page_no, page_total=page_total)
