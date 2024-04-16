from pythainlp.tokenize import word_tokenize
from pythainlp import word_vector
from gensim.models import KeyedVectors

model_path = 'features/thai2vec.bin'
model = KeyedVectors.load_word2vec_format(model_path,binary=True)

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
        print("choiceWord", choiceWord)
    return choiceWord

choiceWord = findSimilarity("ไฟไหม้")
