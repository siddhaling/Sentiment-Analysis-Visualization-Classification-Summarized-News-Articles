from vader import SentimentIntensityAnalyzer
from textSummarizationForNewsArticle_1 import mainSummaryCalling
import numpy as np
import os
import re
from mpl_toolkits.mplot3d import Axes3D
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
import matplotlib.pyplot as plt


stopWords = set(stopwords.words('english'))
stopWords.update(['"', "'", ':', '(', ')', '[', ']', '{', '}']) #'.',  ',', '?', '!', ';'
#path name containing the news files
bbcNewsFldr='BBCNews'

#Identify the noun position
def getNounPositions(type,tagged):
    nounPosi={}
    for item in tagged:
        if item[1]==type:
            nounPosi[item[0]]=-1
    
    for key in nounPosi.keys():
        regExpression=r'\b'+key.lower()+r'\b'
        nounsi=[m.start() for m in re.finditer(regExpression, lineIn.lower())]
        nounPosi[key]=nounsi
    return nounPosi
#obtain words from sentence
def getWords(sentence):
	return word_tokenize(sentence)

#using pos_tag obtain the tags for words
def getTagsForWords(textLn2):
    tokens=word_tokenize(textLn2)
    tagged=pos_tag(tokens)
    return(tagged)
#remove stop words
def stopwordRemove(wordlist):
	stopword_list = set(stopwords.words('english'))
	return [stopped for stopped in wordlist if stopped not in stopword_list]
#get top three nouns and their frequency
def getTop3NounAndFreq(NNP):
    top3Noun=[]*3
    nounSortedByFreq=sorted(NNP.items(), key=lambda item: len(item[1]), reverse=True)    
    for ni in range(len(nounSortedByFreq)):
        if ni>2:
            break
        nounNm=nounSortedByFreq[ni][0]
        freqNm=len(nounSortedByFreq[ni][1])
        top3Noun.append((nounNm,freqNm))
    return(top3Noun)

#read text into a single file
def readFromSingleFile(fullFileNm):
    newsContent=[]
    dataFile=open(fullFileNm)
    for l in dataFile:
        print(len(l))
        if(len(l)<=1):
            continue
        newsContent.append(l.rstrip('\n'))
    dataFile.close()
    return newsContent

#perform the 3D column chart of noun, compound score and summary ratio
def plotMatrix3DColumnNounCompundScoreOccurence(sentiment_scoresForAnArticle):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    nElements=len(sentiment_scoresForAnArticle)
    xs=[i for i in range(10)]
    ys=[sei[0][0][1] for  sei in sentiment_scoresForAnArticle ]
    zs=[0]*nElements
    dx=[0.4]*nElements
    dy=[0.4]*nElements
    dz=[np.abs(sei[1]['compoundScore']) for  sei in sentiment_scoresForAnArticle ]
    colors_ar=[]
    for aSenti in sentiment_scoresForAnArticle:
        if aSenti[1]['compoundScore']>0:
            colors_ar.append('b')
        elif aSenti[1]['compoundScore']==0:
            colors_ar.append('g')
        else:
            colors_ar.append('r')    
    
    ax.bar3d(xs,ys,zs,dx,dy,dz,color=colors_ar)
    ax.plot([],[],color='b',label='Positve Sentiment')
    ax.plot([],[],color='g',label='Neutral Sentiment')
    ax.plot([],[],color='r',label='Negative Sentiment')
    ax.set_xlabel('Noun')
    ax.set_ylabel('Num. of Noun Occurences')
    ax.set_zlabel('Compound Score')
    plt.legend()
    plt.show()    

#perform 3D column chart of noun, positive and negative score
def plotMatrix3DColumnNounPosiNegiScore(sentiment_scoresForAnArticle):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    nElements=len(sentiment_scoresForAnArticle)
    xs=[i for i in range(nElements)]
    ys=[sei[1]['negScore'] for  sei in sentiment_scoresForAnArticle]
    zs=[0]*nElements
    dx=[0.4]*nElements
    dy=[0.01]*nElements
    dz=[sei[1]['posScore'] for  sei in sentiment_scoresForAnArticle ] 
    ax.bar3d(xs,ys,zs,dx,dy,dz)
    
    ax.set_xlabel('Noun')
    ax.set_ylabel('Negative Score')
    ax.set_zlabel('Positive Score')
    plt.legend()
    plt.show()    

cnt=0
percentageOfSummary=[i for i in range(100,0,-10)]
positiveScores=[]
negativeScores=[]
compoundScores=[]
sentiment_scoresForAnArticle=[]
#read the files from give path
for filename in os.listdir(bbcNewsFldr):    
    cnt=cnt+1
    if (cnt>1): 
        break
    text=readFromSingleFile(bbcNewsFldr+'/'+filename)
    lineIn='\n'.join(text)
    
    tagged=getTagsForWords(lineIn)
    NNP=getNounPositions('NNP',tagged)
    top3Noun=getTop3NounAndFreq(NNP)
    #perform the summarization multiple time and compute sentiment information each time
    for pi in percentageOfSummary:
        reducedSummaryWithReplc=mainSummaryCalling(lineIn,pi)    
        review_tokens = [getWords(asdf.lower()) for asdf in reducedSummaryWithReplc]
        stopped_sent = [stopwordRemove(sentence) for sentence in review_tokens]
        sents = []
        for i in stopped_sent:
            asdf = ''
            for j in i:
                asdf = asdf + j + ' '
            sents.append(asdf)
        sid = SentimentIntensityAnalyzer()
        allReviews=' '.join(sent for sent in sents)
        sentiment_scores=sid.polarity_scores(allReviews)
        positiveScores.append(sentiment_scores['posScore'])
        negativeScores.append(sentiment_scores['negScore'])
        compoundScores.append(sentiment_scores['compoundScore'])
        sentiment_scoresForAnArticle.append([top3Noun,sentiment_scores])
        print(sentiment_scores['posScore'])
#plot the 3D column chart
plotMatrix3DColumnNounPosiNegiScore(sentiment_scoresForAnArticle)
#plot the 3D column chart
plotMatrix3DColumnNounCompundScoreOccurence(sentiment_scoresForAnArticle)
