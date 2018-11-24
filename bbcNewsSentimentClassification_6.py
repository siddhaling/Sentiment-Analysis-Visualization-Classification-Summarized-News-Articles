import os
import nltk
import random
from nltk import word_tokenize
from vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

#obtain the words in a sentence
def getWords(sentence):
	return word_tokenize(sentence)
#remove stopwords and retun the list
def stopwordRemove(wordlist):
	stopword_list = set(stopwords.words('english'))
	return [stopped for stopped in wordlist if stopped not in stopword_list]

#reading news text from a single file
def readFromSingleFile(newReadPath,fileNm):
    path=newReadPath+'/'+fileNm
    newsContent=[]
    dataFile=open(path)
    for l in dataFile:
        print(len(l))
        if(len(l)<=1):
            continue
        newsContent.append(l.rstrip('\n'))
    dataFile.close()
    return newsContent

#form the feature vector from the given text files
def formFeaturesFromDocs(document,wordsCollectAsFeatures):
    words=set(document)
    features={}
    for w in wordsCollectAsFeatures:
        features[w]=(w in words)
    return features

#collect file content and compute the sentiments
def collectAllSentiments(bbcNewFldr):
    sentimentScoresForAnArticle=[]
    for filename in os.listdir(bbcNewFldr):
        text=readFromSingleFile(bbcNewFldr,filename)
        newsTokens = [getWords(asdf.lower()) for asdf in text]
        stopWordRmdLst = [stopwordRemove(sentence) for sentence in newsTokens]
        sents = []
        for i in stopWordRmdLst:
            asdf = ''
            for j in i:
                asdf = asdf + j + ' '
            sents.append(asdf)
        sid = SentimentIntensityAnalyzer()
        allReviews=' '.join(sent for sent in sents)
        sentiment_scores=sid.polarity_scores(allReviews)
        sentimentScoresForAnArticle.append(sentiment_scores)    
    return sentimentScoresForAnArticle
    
#path where the text files are kept
bbcNewFldr='BBCNews'
sentimentScoresForAnArticle=collectAllSentiments(bbcNewFldr)

#based on sentiment score prepare documents either positive(1) or negative(0)
documents=[]
for si in sentimentScoresForAnArticle:
    print('working...')
    if si['compoundScore']>=0:
        category=1#'pos'
    else:
        category=0#'neg'  
    documents.append((list(si['wordsWithEmotion']),category))

random.shuffle(documents)

#collect all the words with emotion
allWords=[]
for si in sentimentScoresForAnArticle:
    lowerCaseWords=[w.lower() for w in si['wordsWithEmotion']]
    allWords.extend(lowerCaseWords)
#determine frequency of words using nltk
allWords=nltk.FreqDist(allWords)
print(allWords.most_common(15))
#from feature vector with most common words
wordsCollectAsFeatures=[ai[0] for ai in allWords.most_common(5000)]

#prepare feature vector for each document
featuresets=[(formFeaturesFromDocs(rev,wordsCollectAsFeatures),category) for (rev,category) in documents]
X=[]
y=[]
for i in range(len(featuresets)):
    X.append(list(featuresets[i][0].values()))
    y.append(featuresets[i][1])
#create a classifier and perform cross validation
clf=RandomForestClassifier()
scores=cross_val_score(clf,X,y,cv=5)
print(scores)
print('Accuracy=',scores.mean(),'Std deviation=',scores.std()*2)