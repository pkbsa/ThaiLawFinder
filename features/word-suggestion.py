import pickle
from pythainlp import word_tokenize, tokenize

def findSimilarity(word):
    try:
        # print("word:", word)
        score_th = 0.75
        TLHR_model = pickle.load(open('features/models/w2v400vTLHR.sav', 'rb'))
        TPBS_model = pickle.load(open('features/models/w2v400vtpbs.sav', 'rb'))
        Best_model = pickle.load(open('features/models/w2v400vBEST.sav', 'rb'))
        # print("Open Successful")
        TLHR_similar = TLHR_model.wv.most_similar(word)
        TPBS_similar = TPBS_model.wv.most_similar(word)
        BEST_similar = Best_model.wv.most_similar(word)
        # print("load Successful")
        TLHR_score = [word for word, score in TLHR_similar if score > score_th]
        TPBS_score = [word for word, score in TPBS_similar if score > score_th]
        BEST_score = [word for word, score in BEST_similar if score > score_th]

        all_outputs = [TLHR_score, TPBS_score, BEST_score]
        common_words = set(all_outputs[0]).union(*all_outputs[1:])
        return list(common_words)
    except KeyError:
        return []

def wordSuggestion(sentence):
    cutedSentence = word_tokenize(sentence, engine='deepcut')
    print(cutedSentence)
    wordSuggestion = []
    for i in cutedSentence:
        wordSuggestion = wordSuggestion + findSimilarity(i)
    print(wordSuggestion)

    return wordSuggestion

wordSuggestion("ผ")