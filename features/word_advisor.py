from pythainlp.tokenize import word_tokenize
from gensim.models import KeyedVectors

import json

model_path = 'features/thai2vec.bin'
model = KeyedVectors.load_word2vec_format(model_path,binary=True)

def findSimilarity(sentence):

    with open('config.json', 'r') as f:
        config = json.load(f)
    WORD_ADVISOR_THRESHOLD = config['WORD_ADVISOR_THRESHOLD']
    WORD_ADVISOR_MAX_EACH_WORD = config['WORD_ADVISOR_MAX_EACH_WORD']
    WORD_ADVISOR_MAX_WORD = config['WORD_ADVISOR_MAX_WORD']

    cutedSentence = word_tokenize(sentence, engine='deepcut')

    choiceWord = []
    maxword = 0
    for word in cutedSentence:
        try:
            similar = model.most_similar_cosmul(positive=["คดี","กฎหมาย",word], negative=[])
        except:
            similar=[]
        count=0
        for WORD, THRESHOLD in similar:
            # print(l, k)
            if THRESHOLD > WORD_ADVISOR_THRESHOLD and count <=WORD_ADVISOR_MAX_EACH_WORD and WORD not in choiceWord and maxword <= WORD_ADVISOR_MAX_WORD:
                choiceWord.append(WORD)
                count+=1
                maxword+=1
        # print("-----")
        print("choiceWord", choiceWord)
    return choiceWord


